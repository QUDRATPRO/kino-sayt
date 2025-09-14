from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
import uuid
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Movie, Purchase, StreamToken
from .forms import CustomUser  # импорт вашей формы




# --- User Login ---
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_blocked:
                return JsonResponse({"detail": "Account is blocked."}, status=403)
            login(request, user)
            return JsonResponse({"detail": "Login successful", "user": user.username})
        else:
            return JsonResponse({"detail": "Invalid credentials"}, status=401)
    return JsonResponse({"detail": "Only POST method allowed"}, status=405)



def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})



# --- Movie List ---
def movie_list_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)

    movies = Movie.objects.all()
    data = [{
        "id": m.id,
        "title": m.title,
        "description": m.description,
        "thumbnail": m.thumbnail.url if m.thumbnail else None,
        "price": m.price
    } for m in movies]
    return JsonResponse({"movies": data})


# --- Movie Detail ---
def movie_detail_view(request, movie_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return JsonResponse({"detail": "Movie not found"}, status=404)

    data = {
        "id": movie.id,
        "title": movie.title,
        "description": movie.description,
        "thumbnail": movie.thumbnail.url if movie.thumbnail else None,
        "price": movie.price,
        "created_at": movie.created_at
    }
    return JsonResponse(data)


# --- Purchase Movie ---
@csrf_exempt
def purchase_movie_view(request, movie_id):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required"}, status=401)

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return JsonResponse({"detail": "Movie not found"}, status=404)

        if Purchase.objects.filter(user=request.user, movie=movie).exists():
            return JsonResponse({"detail": "Already purchased or requested"}, status=400)

        purchase = Purchase.objects.create(user=request.user, movie=movie)
        return JsonResponse({"detail": "Purchase request created", "purchase_id": purchase.id})

    return JsonResponse({"detail": "Only POST method allowed"}, status=405)


# --- Generate Stream Token ---
def generate_stream_token_view(request, movie_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)

    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return JsonResponse({"detail": "Movie not found"}, status=404)

    if not request.user.is_premium:
        return JsonResponse({"detail": "Not a premium user"}, status=403)

    if not Purchase.objects.filter(user=request.user, movie=movie, approved=True).exists():
        return JsonResponse({"detail": "Movie not purchased or not approved"}, status=403)

    expires_at = timezone.now() + timezone.timedelta(minutes=30)
    token_obj, created = StreamToken.objects.update_or_create(
        user=request.user,
        movie=movie,
        defaults={"expires_at": expires_at, "token": uuid.uuid4()}
    )

    return JsonResponse({
        "token": str(token_obj.token),
        "expires_at": token_obj.expires_at
    })

User = get_user_model()

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def approve_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    purchase.approved = True
    purchase.save()

    # Admin action log
    AdminActionLog.objects.create(
        admin=request.user,
        action=f"Approved purchase id {purchase.id} for user {purchase.user.username}"
    )

    messages.success(request, f"Purchase #{purchase.id} approved successfully.")
    return redirect('admin_dashboard')  # Admin panelingiz sahifasiga yo'naltiring

@login_required
@user_passes_test(is_admin)
def approve_premium_request(request, request_id):
    premium_request = get_object_or_404(PremiumRequest, id=request_id)
    premium_request.approved = True
    premium_request.save()

    user = premium_request.user
    user.is_premium = True
    user.save()

    AdminActionLog.objects.create(
        admin=request.user,
        action=f"Approved premium request for user {user.username}"
    )

    messages.success(request, f"Premium status approved for user {user.username}.")
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'No reason provided')
        user.is_blocked = True
        user.save()

        BlockedUser.objects.update_or_create(user=user, defaults={
            'reason': reason,
            'blocked_at': timezone.now()
        })

        AdminActionLog.objects.create(
            admin=request.user,
            action=f"Blocked user {user.username}. Reason: {reason}"
        )

        messages.success(request, f"User {user.username} has been blocked.")
        return redirect('admin_dashboard')

    # GET request uchun forma ko'rsatish (agar kerak bo'lsa)
    return render(request, 'admin/block_user.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = False
    user.save()

    BlockedUser.objects.filter(user=user).delete()

    AdminActionLog.objects.create(
        admin=request.user,
        action=f"Unblocked user {user.username}"
    )

    messages.success(request, f"User {user.username} has been unblocked.")
    return redirect('admin_dashboard')