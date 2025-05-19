from django.urls import path

from payments.views import (
    PaymentSuccessView,
    PaymentCancelView
)


urlpatterns = [
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("cancel/", PaymentCancelView.as_view(), name="cancel"),
]

app_name = "payments"
