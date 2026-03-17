"""
URL patterns for the users app.

Mounted at /api/users/ in config/urls.py.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    MeView,
    RegisterView,
    UserDetailView,
    UserListView,
)

app_name = "users"

urlpatterns = [
    # Public auth
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Authenticated user — own profile
    path("me/", MeView.as_view(), name="me"),

    # Admin — user management
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
