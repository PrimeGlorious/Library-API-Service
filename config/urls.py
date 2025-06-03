"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views.
For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from config import settings

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Django Admin & DRF Auth
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "api-auth/",
        include(
            "rest_framework.urls",
            namespace="rest_framework",
        ),
    ),
    # Application Endpoints
    path(
        "api/library/",
        include(
            "books.urls",
            namespace="books",
        ),
    ),
    path(
        "api/borrow/",
        include(
            "borrowings.urls",
            namespace="borrowings",
        ),
    ),
    path(
        "api/user/",
        include(
            "user.urls",
            namespace="user",
        ),
    ),
    path(
        "api/payments/",
        include(
            "payments.urls",
            namespace="payments",
        ),
    ),
    # API Documentation
    path(
        "api/doc/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/doc/swagger/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
        ),
        name="swagger-ui",
    ),
    path(
        "api/doc/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema",
        ),
        name="redoc",
    ),
]

# Media files (only in DEBUG)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
