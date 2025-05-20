from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True,
                                     min_length=5)
    password2 = serializers.CharField(style={"input_type": "password"},
                                      write_only=True,
                                      min_length=5)

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

class EmailVerificationSerializer(serializers.ModelSerializer):

    token = serializers.CharField(max_length=555)

    class Meta:
        model = get_user_model()
        fields = ["token"]
