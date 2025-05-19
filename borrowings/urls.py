from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowings.views import BorrowingsViewSet


router = DefaultRouter()
router.register("borrowings", BorrowingsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowings"
