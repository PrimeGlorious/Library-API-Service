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


class PaymentSuccessView(APIView):
    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"detail": "Session ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.filter(session_id=session_id).first()
        if not payment:
            return Response(
                {"detail": "Payment session not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        payment.status = Payment.Status.PAID
        payment.save()

        return Response({"detail": "Payment completed successfully"})

class PaymentCancelView(APIView):
    def get(self, request):
        return Response({"detail": "Payment was cancelled. "
                                   "You can pay later within 24 hours."})
