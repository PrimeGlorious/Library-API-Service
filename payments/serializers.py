from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
            "created_at",
        )
        read_only_fields = (
            "session_url",
            "session_id",
            "money_to_pay",
            "borrowing",
            "status",
            "type",
            "created_at",
        )


class PaymentNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "session_url",
            "money_to_pay",
            "created_at",
        )
