"""
User views.

Auth flows:

  Registration (2 steps):
    POST /api/users/register/         — create inactive account + send OTP
    POST /api/users/register/verify/  — email + OTP code → activate + return JWT

  Login (2 steps):
    POST /api/users/login/            — email + password → send OTP (no JWT yet)
    POST /api/users/login/verify/     — email + OTP code → return JWT

  Profile:
    GET   /api/users/me/   — read own profile
    PATCH /api/users/me/   — update own profile

  Token:
    POST /api/users/token/refresh/    — refresh JWT

  Admin:
    GET    /api/users/              — list all users
    POST   /api/users/              — create user with any role
    GET    /api/users/{id}/         — retrieve user
    PATCH  /api/users/{id}/         — update user
    DELETE /api/users/{id}/         — delete user
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

from .emails import send_otp_email
from .models import OTPCode, User
from .permissions import IsAdminRole
from .serializers import (
    AdminUserSerializer,
    LoginSerializer,
    LoginVerifySerializer,
    RegisterSerializer,
    RegisterVerifySerializer,
    UserSerializer,
)


# ---------------------------------------------------------------------------
# Register — step 1: create inactive account + send OTP
# ---------------------------------------------------------------------------

@extend_schema(
    tags=["Auth"],
    summary="Register — step 1: create account",
    description=(
        "Creates an inactive user account and sends a 6-digit OTP to the email. "
        "The account cannot be used until step 2 (verify) is completed."
    ),
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(description="Account created, OTP sent"),
        400: OpenApiResponse(description="Validation errors"),
    },
    examples=[
        OpenApiExample(
            "Register example",
            value={
                "email": "alice@example.com",
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
    """Step 1 — creates an inactive account and sends an OTP."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        otp = OTPCode.generate(user.email)
        send_otp_email(user.email, otp.code, OTPCode.EXPIRY_MINUTES)

        return Response(
            {"detail": f"Compte créé. Un code de vérification a été envoyé à {user.email}."},
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Register — step 2: verify OTP → activate account + return JWT
# ---------------------------------------------------------------------------

@extend_schema(
    tags=["Auth"],
    summary="Register — step 2: verify OTP",
    description=(
        "Submits the OTP received by email. "
        "On success, the account is activated and JWT tokens are returned immediately."
    ),
    request=RegisterVerifySerializer,
    responses={
        200: OpenApiResponse(
            description="Account activated — JWT tokens returned",
            response={
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "user": {"type": "object"},
                },
            },
        ),
        400: OpenApiResponse(description="Invalid or expired OTP"),
    },
    examples=[
        OpenApiExample(
            "Register verify example",
            value={"email": "alice@example.com", "code": "482910"},
            request_only=True,
        ),
    ],
)
class RegisterVerifyView(APIView):
    """Step 2 — validates OTP, activates account, returns JWT tokens."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        return Response(
            {
                "access": data["access"],
                "refresh": data["refresh"],
                "user": UserSerializer(data["user"], context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Login — step 1: validate credentials + send OTP
# ---------------------------------------------------------------------------

@extend_schema(
    tags=["Auth"],
    summary="Login — step 1: validate credentials",
    description=(
        "Authenticates email and password. "
        "If valid, sends a 6-digit OTP to the email. "
        "JWT tokens are only issued after step 2 (verify)."
    ),
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description="Credentials valid, OTP sent"),
        400: OpenApiResponse(description="Invalid credentials or inactive account"),
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
    """Step 1 — validates credentials and sends an OTP. No JWT returned yet."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        otp = OTPCode.generate(user.email)
        send_otp_email(user.email, otp.code, OTPCode.EXPIRY_MINUTES)

        return Response(
            {"detail": f"Code de vérification envoyé à {user.email}."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Login — step 2: verify OTP → return JWT
# ---------------------------------------------------------------------------

@extend_schema(
    tags=["Auth"],
    summary="Login — step 2: verify OTP",
    description=(
        "Submits the OTP received by email after login step 1. "
        "On success, returns JWT access and refresh tokens."
    ),
    request=LoginVerifySerializer,
    responses={
        200: OpenApiResponse(
            description="JWT tokens returned",
            response={
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "user": {"type": "object"},
                },
            },
        ),
        400: OpenApiResponse(description="Invalid or expired OTP"),
    },
    examples=[
        OpenApiExample(
            "Login verify example",
            value={"email": "alice@example.com", "code": "193847"},
            request_only=True,
        ),
    ],
)
class LoginVerifyView(APIView):
    """Step 2 — validates OTP and returns JWT tokens."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        return Response(
            {
                "access": data["access"],
                "refresh": data["refresh"],
                "user": UserSerializer(data["user"], context={"request": request}).data,
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
