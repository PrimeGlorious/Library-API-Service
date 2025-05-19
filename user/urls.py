from django.urls import path

from user.views import ManageUserView, SignUp, VerifyEmail

app_name = "user"

urlpatterns = [
    path("me/", ManageUserView.as_view(), name="manage"),
    path("register/", SignUp.as_view(), name="signup"),
    path("email-verify/", VerifyEmail.as_view(), name="email-verify"),
]
