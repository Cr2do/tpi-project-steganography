"""
URL patterns for the users app.

Mounted at /api/users/ in config/urls.py.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginVerifyView,
    LoginView,
    MeView,
    RegisterVerifyView,
    RegisterView,
    UserDetailView,
    UserListView,
)

app_name = "users"

urlpatterns = [
    # Registration (2 steps)
    path("register/",        RegisterView.as_view(),       name="register"),
    path("register/verify/", RegisterVerifyView.as_view(), name="register-verify"),

    # Login (2 steps)
    path("login/",           LoginView.as_view(),          name="login"),
    path("login/verify/",    LoginVerifyView.as_view(),    name="login-verify"),

    # Token refresh
    path("token/refresh/",   TokenRefreshView.as_view(),   name="token-refresh"),

    # Authenticated user — own profile
    path("me/",              MeView.as_view(),              name="me"),

    # Admin — user management
    path("",                 UserListView.as_view(),        name="user-list"),
    path("<int:pk>/",        UserDetailView.as_view(),      name="user-detail"),
]
