"""
User views.

Endpoints:
  POST   /api/users/register/     — public registration
  POST   /api/users/login/        — obtain JWT tokens
  GET    /api/users/me/           — authenticated user reads their own profile
  PATCH  /api/users/me/           — authenticated user updates their own profile
  GET    /api/users/              — admin: list all users
  POST   /api/users/              — admin: create a user with any role
  GET    /api/users/{id}/         — admin: retrieve a specific user
  PATCH  /api/users/{id}/         — admin: update a specific user
  DELETE /api/users/{id}/         — admin: delete a specific user
"""
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsAdminRole
from .serializers import (
    AdminUserSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@extend_schema(
    tags=["Auth"],
    summary="Register a new user",
    description=(
        "Creates a new user account with the role set to 'user'. "
        "No authentication is required."
    ),
    request=RegisterSerializer,
    responses={
        201: UserSerializer,
        400: OpenApiResponse(description="Validation errors"),
    },
    examples=[
        OpenApiExample(
            "Registration example",
            value={
                "email": "alice@example.com",
                "username": "alice",
                "first_name": "Alice",
                "last_name": "Smith",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
            request_only=True,
        ),
    ],
)
class RegisterView(generics.CreateAPIView):
    """Public endpoint — creates a regular user account."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = UserSerializer(user, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@extend_schema(
    tags=["Auth"],
    summary="Login — obtain JWT tokens",
    description=(
        "Authenticates the user with email and password. "
        "Returns a JWT access token (short-lived) and a refresh token (long-lived)."
    ),
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            description="JWT tokens + user info",
            response={
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "email": {"type": "string"},
                            "role": {"type": "string"},
                        },
                    },
                },
            },
        ),
        400: OpenApiResponse(description="Invalid credentials"),
    },
    examples=[
        OpenApiExample(
            "Login example",
            value={"email": "alice@example.com", "password": "StrongPass123!"},
            request_only=True,
        ),
    ],
)
class LoginView(APIView):
    """Public endpoint — returns JWT access and refresh tokens."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = data["user"]

        return Response(
            {
                "access": data["access"],
                "refresh": data["refresh"],
                "user": UserSerializer(user, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Me (authenticated user — own profile)
# ---------------------------------------------------------------------------

@extend_schema_view(
    get=extend_schema(
        tags=["Users"],
        summary="Get my profile",
        description="Returns the profile of the currently authenticated user.",
        responses={200: UserSerializer},
    ),
    patch=extend_schema(
        tags=["Users"],
        summary="Update my profile",
        description=(
            "Updates editable fields of the authenticated user's profile. "
            "Role and email cannot be changed through this endpoint."
        ),
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Validation errors"),
        },
    ),
)
class MeView(generics.RetrieveUpdateAPIView):
    """Authenticated user reads or updates their own profile."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


# ---------------------------------------------------------------------------
# User list + create (admin only)
# ---------------------------------------------------------------------------

@extend_schema_view(
    get=extend_schema(
        tags=["Admin — Users"],
        summary="List all users",
        description="Returns a paginated list of all user accounts. Admin role required.",
        responses={200: AdminUserSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="page",
                description="Page number for pagination.",
                required=False,
                type=int,
            ),
        ],
    ),
    post=extend_schema(
        tags=["Admin — Users"],
        summary="Create a user (admin)",
        description=(
            "Creates a new user with any role. "
            "The password must be supplied; it will be hashed before storage."
        ),
        request=AdminUserSerializer,
        responses={
            201: AdminUserSerializer,
            400: OpenApiResponse(description="Validation errors"),
        },
    ),
)
class UserListView(generics.ListCreateAPIView):
    """Admin-only: list all users or create a new user with any role."""

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]

    def perform_create(self, serializer):
        password = self.request.data.get("password")
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])


# ---------------------------------------------------------------------------
# User detail (admin only)
# ---------------------------------------------------------------------------

@extend_schema_view(
    get=extend_schema(
        tags=["Admin — Users"],
        summary="Retrieve a user",
        description="Returns all details for a specific user. Admin role required.",
        responses={
            200: AdminUserSerializer,
            404: OpenApiResponse(description="User not found"),
        },
    ),
    patch=extend_schema(
        tags=["Admin — Users"],
        summary="Update a user",
        description=(
            "Partially updates a user account, including role and is_active. "
            "Admin role required."
        ),
        request=AdminUserSerializer,
        responses={
            200: AdminUserSerializer,
            400: OpenApiResponse(description="Validation errors"),
            404: OpenApiResponse(description="User not found"),
        },
    ),
    delete=extend_schema(
        tags=["Admin — Users"],
        summary="Delete a user",
        description="Permanently deletes a user account. Admin role required.",
        responses={
            204: OpenApiResponse(description="User deleted"),
            404: OpenApiResponse(description="User not found"),
        },
    ),
)
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin-only: retrieve, update, or delete any user by id."""

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]
    http_method_names = ["get", "patch", "delete", "head", "options"]
