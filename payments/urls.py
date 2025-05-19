from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentSuccessView,
    PaymentCancelView,
    PaymentViewSet
)


router = DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("cancel/", PaymentCancelView.as_view(), name="cancel"),
]

app_name = "payments"
