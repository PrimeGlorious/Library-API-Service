from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment


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
