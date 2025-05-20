from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from user.views import ManageUserView, SignUp, VerifyEmail

app_name = "user"

urlpatterns = [
    path("me/", ManageUserView.as_view(), name="manage"),
    path("register/", SignUp.as_view(), name="signup"),
    path("email-verify/", VerifyEmail.as_view(), name="email-verify"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
