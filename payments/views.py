from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from orders.models import Order
from users.views import get_user_by_request

from .models import Payment
from .serializers import PaymentSerializer


def get_payment_for_user(pk, user):
    try:
        return Payment.objects.select_related("order").get(pk=pk, order__user=user)
    except Payment.DoesNotExist:
        return None


@api_view(["POST"])
def payments_view(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    order_id = request.data.get("order_id")
    payment_type = request.data.get("payment_type")
    if payment_type not in Payment.PaymentType.values:
        return Response(
            {"error": "payment_type must be mock_wechat, mock_alipay, or mock_balance."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        order = Order.objects.get(pk=order_id, user=user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.Status.PENDING_PAYMENT:
        return Response(
            {"error": "Only pending_payment orders can create payments."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payment = Payment.objects.create(
        order=order,
        payment_type=payment_type,
        amount=order.total_amount,
        status=Payment.Status.PENDING,
    )
    return Response({"payment": PaymentSerializer(payment).data}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def payment_success_view(request, pk):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    payment = get_payment_for_user(pk, user)
    if not payment:
        return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

    if payment.order.status != Order.Status.PENDING_PAYMENT:
        return Response(
            {"error": "Only pending_payment orders can be paid successfully."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if payment.status != Payment.Status.PENDING:
        return Response(
            {"error": "Only pending payments can be marked as success."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payment.status = Payment.Status.SUCCESS
    payment.paid_at = timezone.now()
    payment.save(update_fields=["status", "paid_at"])
    payment.order.status = Order.Status.PAID
    payment.order.save(update_fields=["status"])

    return Response({"payment": PaymentSerializer(payment).data})


@api_view(["POST"])
def payment_fail_view(request, pk):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    payment = get_payment_for_user(pk, user)
    if not payment:
        return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

    if payment.status != Payment.Status.PENDING:
        return Response(
            {"error": "Only pending payments can be marked as failed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payment.status = Payment.Status.FAILED
    payment.save(update_fields=["status"])
    return Response({"payment": PaymentSerializer(payment).data})
