from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTPCode, User, UserRole


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_otp(email: str, code: str) -> OTPCode:
    """
    Shared OTP validation logic.
    Increments attempts, checks validity, marks as used on success.
    Raises ValidationError on any failure.
    """
    otp = (
        OTPCode.objects.filter(email=email, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if otp is None:
        raise serializers.ValidationError({"code": "Aucun code OTP en attente pour cet email."})

    otp.attempts += 1
    otp.save(update_fields=["attempts"])

    if not otp.is_valid:
        raise serializers.ValidationError({"code": "Ce code est expiré ou invalide."})

    if otp.code != code:
        remaining = OTPCode.MAX_ATTEMPTS - otp.attempts
        if remaining > 0:
            raise serializers.ValidationError(
                {"code": f"Code incorrect. {remaining} tentative(s) restante(s)."}
            )
        raise serializers.ValidationError(
            {"code": "Code incorrect. Veuillez en demander un nouveau."}
        )

    otp.is_used = True
    otp.save(update_fields=["is_used"])
    return otp


def _jwt_for_user(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

class RegisterSerializer(serializers.ModelSerializer):
    """
    Creates a user with is_active=False.
    Account activation happens via RegisterVerifySerializer.
    """
    password = serializers.CharField(
        write_only=True, required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "birth_date", "password", "password_confirm"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.role = UserRole.USER
        user.is_active = False   # activated only after OTP verification
        user.set_password(password)
        user.save()
        return user


class RegisterVerifySerializer(serializers.Serializer):
    """
    Verifies the OTP sent after registration.
    On success: activates the account and returns JWT tokens.
    """
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        email = attrs["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Aucun compte trouvé pour cet email."})

        if user.is_active:
            raise serializers.ValidationError({"email": "Ce compte est déjà activé."})

        _validate_otp(email, attrs["code"])

        user.is_active = True
        user.save(update_fields=["is_active"])

        tokens = _jwt_for_user(user)
        return {"user": user, **tokens}


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class LoginSerializer(serializers.Serializer):
    """
    Validates email + password.
    Does NOT return JWT tokens — those are issued after OTP verification.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        # Check if account exists but is inactive (not yet verified)
        try:
            user_obj = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"non_field_errors": "Email ou mot de passe invalide."})

        if not user_obj.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": "Ce compte n'est pas encore activé. Vérifiez votre email d'inscription."}
            )

        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError({"non_field_errors": "Email ou mot de passe invalide."})

        return {"user": user}


class LoginVerifySerializer(serializers.Serializer):
    """
    Verifies the OTP sent after login.
    On success: returns JWT tokens.
    """
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        email = attrs["email"]

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Aucun compte actif trouvé pour cet email."})

        _validate_otp(email, attrs["code"])

        tokens = _jwt_for_user(user)
        return {"user": user, **tokens}


# ---------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "birth_date", "role"]
        read_only_fields = ["id", "email", "role"]


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=False, allow_blank=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "birth_date", "role", "is_active", "password"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
