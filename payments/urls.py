from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentCancelView,
    PaymentViewSet,
    StripeWebhookView
)


router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("cancel/", PaymentCancelView.as_view(), name="cancel"),
]

app_name = "payments"
