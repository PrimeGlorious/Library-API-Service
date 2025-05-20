import stripe
from django.conf import settings
from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from payments.serializers import PaymentSerializer


class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.borrowing.user == request.user


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)


class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.headers.get("Stripe-Signature")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session.get("id")
            payment = Payment.objects.filter(session_id=session_id).first()
            if payment and payment.status != Payment.Status.PAID:
                payment.status = Payment.Status.PAID
                payment.save()

                borrowing = payment.borrowing
                if borrowing and not borrowing.is_paid:
                    borrowing.is_paid = True
                    borrowing.save()
                    borrowing.book.inventory -= 1
                    borrowing.book.save()


        return Response(status=status.HTTP_200_OK)


class PaymentCancelView(APIView):
    def get(self, request):
        return Response({"detail": "Payment was cancelled. "
                                   "You can pay later within 24 hours."})
