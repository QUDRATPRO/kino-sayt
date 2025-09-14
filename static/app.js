const BASE_URL = "http://localhost:8000/api"; // kerakli holatda o‘zgartiring
let token = localStorage.getItem("access");

// DOM elementlar
const authSection = document.getElementById("authSection");
const loginBox = document.getElementById("loginBox");
const registerBox = document.getElementById("registerBox");
const showRegister = document.getElementById("showRegister");
const showLogin = document.getElementById("showLogin");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const moviesSection = document.getElementById("moviesSection");
const moviesContainer = document.getElementById("moviesContainer");
const logoutBtn = document.getElementById("logoutBtn");
const logoutBtn2 = document.getElementById("logoutBtn2");

const movieDetailSection = document.getElementById("movieDetailSection");
const backBtn = document.getElementById("backBtn");
const purchaseBtn = document.getElementById("purchaseBtn");
const videoPlayer = document.getElementById("videoPlayer");
const videoContainer = document.getElementById("videoContainer");
const movieTitle = document.getElementById("movieTitle");
const movieDescription = document.getElementById("movieDescription");

// UI funksiyalar
function showSection(section) {
  [authSection, moviesSection, movieDetailSection].forEach(s => s.classList.add("hidden"));
  section.classList.remove("hidden");
}

// Auth UI
showRegister.onclick = () => {
  loginBox.classList.add("hidden");
  registerBox.classList.remove("hidden");
};
showLogin.onclick = () => {
  registerBox.classList.add("hidden");
  loginBox.classList.remove("hidden");
};

// Logout
function logout() {
  localStorage.removeItem("access");
  token = null;
  showSection(authSection);
}
logoutBtn.onclick = logout;
logoutBtn2.onclick = logout;

// Login
loginForm.onsubmit = async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const res = await fetch(`${BASE_URL}/login/`, {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password}),
  });

  if (res.ok) {
    const data = await res.json();
    token = data.access;
    localStorage.setItem("access", token);
    loadMovies();
  } else {
    alert("Login xato!");
  }
};

// Register
registerForm.onsubmit = async (e) => {
  e.preventDefault();
  const username = document.getElementById("regUsername").value;
  const email = document.getElementById("regEmail").value;
  const password = document.getElementById("regPassword").value;
  const res = await fetch(`${BASE_URL}/register/`, {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, email, password}),
  });

  if (res.ok) {
    alert("Ro'yxatdan o'tdingiz. Login qiling.");
    showLogin.click();
  } else {
    alert("Ro'yxatdan o'tishda xatolik.");
  }
};

// Load movies
async function loadMovies() {
  const res = await fetch(`${BASE_URL}/movies/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.ok) {
    const movies = await res.json();
    moviesContainer.innerHTML = '';
    movies.forEach(movie => {
      const div = document.createElement("div");
      div.className = "movie-card";
      div.innerHTML = `<h3>${movie.title}</h3><p>${movie.description}</p>`;
      div.onclick = () => showMovieDetail(movie);
      moviesContainer.appendChild(div);
    });
    showSection(moviesSection);
  } else {
    logout();
  }
}

// Movie detail
let currentMovie = null;
function showMovieDetail(movie) {
  currentMovie = movie;
  movieTitle.textContent = movie.title;
  movieDescription.textContent = movie.description;
  videoContainer.classList.add("hidden");
  showSection(movieDetailSection);
}

// Back
backBtn.onclick = () => {
  showSection(moviesSection);
};

// Purchase and view video
purchaseBtn.onclick = async () => {
  if (!currentMovie) return;
  const purchaseRes = await fetch(`${BASE_URL}/purchase/${currentMovie.id}/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const tokenRes = await fetch(`${BASE_URL}/stream/token/${currentMovie.id}/`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (tokenRes.ok) {
    const tokenData = await tokenRes.json();
    const streamToken = tokenData.token;
    const videoUrl = `/media/hls/${currentMovie.slug}/index.m3u8?token=${streamToken}`;
    videoPlayer.src = videoUrl;
    videoContainer.classList.remove("hidden");
  } else {
    const err = await tokenRes.json();
    alert(err.detail || "Ko‘rish uchun ruxsat yo‘q");
  }
};

// Init
if (token) {
  loadMovies();
} else {
  showSection(authSection);
}
