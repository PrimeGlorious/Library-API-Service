import jwt
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, response
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import time

from user.serializers import (
    UserSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
)
from user.utils import Util
from user.permissions import IsValidateOrDontHaveAccess


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsValidateOrDontHaveAccess, IsAuthenticated)

    def get_object(self):
        return self.request.user


class SignUp(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = serializer.data

        # getting tokens
        user_email = get_user_model().objects.get(email=user["email"])

        payload = {
            "user_id": user_email.id,
            "exp": int(time.time()) + 600,  # 10 minutes from now
            "iat": int(time.time()),
        }
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # send email for user verification
        current_site = get_current_site(request).domain
        relative_link = reverse("user:email-verify")
        absurl = "http://" + current_site + relative_link + "?token=" + access_token
        email_body = (
            f"Hi {user_email} Use the link below to verify your email \n" + absurl
        )
        data = {
            "email_body": email_body,
            "to_email": user["email"],
            "email_subject": "Verify your email",
        }

        Util.send_email(data=data)

        return response.Response({"user_data": user}, status=status.HTTP_201_CREATED)


class VerifyEmail(GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    token_param_config = openapi.Parameter(
        "token",
        in_=openapi.IN_QUERY,
        description="Email verification token",
        type=openapi.TYPE_STRING,
        required=True,
    )

    @swagger_auto_schema(
        manual_parameters=[token_param_config],
        responses={
            200: openapi.Response(
                description="Email successfully verified",
                examples={"application/json": {"email": "Successfully activated"}},
            ),
            400: openapi.Response(
                description="Invalid or expired token",
                examples={"application/json": {"error": "Activation Expired"}},
            ),
        },
    )
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = get_user_model().objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return response.Response(
                {"email": "Successfully activated"}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError:
            return response.Response(
                {"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError:
            return response.Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationEmail(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResendVerificationSerializer

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return response.Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = get_user_model().objects.get(email=email)
            if user.is_verified:
                return response.Response(
                    {"message": "User is already verified"}, status=status.HTTP_200_OK
                )

            # Generate new verification token
            payload = {
                "user_id": user.id,
                "exp": int(time.time()) + 600,  # 10 minutes from now
                "iat": int(time.time()),
            }
            access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            # Send verification email
            current_site = get_current_site(request).domain
            relative_link = reverse("user:email-verify")
            absurl = "http://" + current_site + relative_link + "?token=" + access_token
            email_body = (
                f"Hi {user} Use the link below to verify your email \n" + absurl
            )
            data = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "Verify your email",
            }

            Util.send_email(data=data)

            return response.Response(
                {"message": "Verification email has been resent"},
                status=status.HTTP_200_OK,
            )

        except get_user_model().DoesNotExist:
            return response.Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
