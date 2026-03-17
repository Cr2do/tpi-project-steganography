from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserRole


class RegisterSerializer(serializers.ModelSerializer):
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
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs.get("email"),
            password=attrs.get("password"),
        )
        if not user:
            raise serializers.ValidationError({"non_field_errors": "Email ou mot de passe invalide."})
        if not user.is_active:
            raise serializers.ValidationError({"non_field_errors": "Ce compte est désactivé."})

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


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
