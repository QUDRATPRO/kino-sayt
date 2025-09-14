from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.get_user_model, name='profile'),
    path('movies/', views.movie_list_view, name='movie_list'),
    path('movie/<int:movie_id>/', views.movie_detail_view, name='movie_detail'),
    path('purchase/<int:movie_id>/', views.purchase_movie_view, name='purchase_movie'),
    path('admin/approve-purchase/<int:purchase_id>/', views.approve_purchase, name='approve_purchase'),
    path('admin/approve-premium/<int:request_id>/', views.approve_premium_request, name='approve_premium'),
    path('admin/block-user/<int:user_id>/', views.block_user, name='block_user'),
    path('admin/unblock-user/<int:user_id>/', views.unblock_user, name='unblock_user'),
]
