import stripe
from decimal import Decimal
from django.conf import settings
from django.urls import reverse

from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

FINE_MULTIPLIER = 2

SUCCESS_URL_TEMPLATE = "borrowings:borrowing-detail"
CANCEL_URL_TEMPLATE = "payments:cancel"


def get_total_amount_and_type(borrowing, is_fine=False, overdue_days=0):
    if is_fine:
        total_amount = (
            Decimal(overdue_days) * borrowing.book.daily_fee * FINE_MULTIPLIER
        )
        payment_type = Payment.Type.FINE
    else:
        total_days = (borrowing.expected_return_date - borrowing.borrow_date).days
        total_amount = borrowing.book.daily_fee * Decimal(total_days)
        payment_type = Payment.Type.PAYMENT
    return total_amount, payment_type


def get_success_url(request, borrowing):
    return request.build_absolute_uri(
        reverse(SUCCESS_URL_TEMPLATE, args=[borrowing.id])
    )


def get_cancel_url(request):
    return request.build_absolute_uri(
        reverse(CANCEL_URL_TEMPLATE)
    ) + "?session_id={CHECKOUT_SESSION_ID}"


def create_stripe_payment_session(borrowing, request, is_fine=False, overdue_days=0):
    total_amount, payment_type = get_total_amount_and_type(borrowing, is_fine, overdue_days)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(total_amount * 100),
                    "product_data": {
                        "name": f"Payment for Borrowing ID {borrowing.id}"
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=get_success_url(request, borrowing),
        cancel_url=get_cancel_url(request),
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_amount,
        type=payment_type,
    )

    return payment
