from rest_framework import serializers
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, min_length=5
    )
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, min_length=5
    )

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "password2", "is_staff")
        read_only_fields = ("is_staff",)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Password don`t match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=555)

    def validate_token(self, value):
        try:
            payload = jwt.decode(value, settings.SECRET_KEY, algorithms=["HS256"])
            user = get_user_model().objects.get(id=payload["user_id"])
            return value
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Activation Expired")
        except jwt.exceptions.DecodeError:
            raise serializers.ValidationError("Invalid token")
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("User not found")


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = get_user_model().objects.get(email=value)
            if user.is_verified:
                raise serializers.ValidationError("User is already verified")
            return value
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
