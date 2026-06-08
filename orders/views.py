from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cart.models import CartItem
from users.models import Coupon
from users.views import get_user_by_request

from .models import Order, OrderItem
from .serializers import OrderSerializer


def get_order_for_user(pk, user):
    try:
        return (
            Order.objects.select_related("user", "merchant", "driver")
            .prefetch_related("items")
            .get(pk=pk, user=user)
        )
    except Order.DoesNotExist:
        return None


def build_order_no():
    return f"ORD{uuid4().hex[:12].upper()}"


@api_view(["GET", "POST"])
def orders_view(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    if request.method == "GET":
        orders = (
            Order.objects.filter(user=user)
            .select_related("user", "merchant", "driver")
            .prefetch_related("items")
        )
        return Response({"orders": OrderSerializer(orders, many=True).data})

    delivery_type = request.data.get("delivery_type")
    if delivery_type not in Order.DeliveryType.values:
        return Response(
            {"error": "delivery_type must be self_pickup or delivery."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart_items = (
        CartItem.objects.filter(user=user)
        .select_related("dish", "dish__merchant")
        .order_by("id")
    )
    if not cart_items.exists():
        return Response(
            {"error": "Cart is empty."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    merchant = cart_items[0].dish.merchant
    merchant_id = request.data.get("merchant_id")
    if merchant_id and str(merchant.id) != str(merchant_id):
        return Response(
            {"error": "Selected store does not match cart dishes."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if any(item.dish.merchant_id != merchant.id for item in cart_items):
        return Response(
            {"error": "All cart items must belong to the same merchant."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    for item in cart_items:
        if item.dish.stock < item.quantity:
            return Response(
                {"error": f"Dish stock is insufficient: {item.dish.name}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    coupon = None
    coupon_id = request.data.get("coupon_id")
    if coupon_id:
        try:
            coupon = Coupon.objects.get(pk=coupon_id, issued_to=user)
        except Coupon.DoesNotExist:
            return Response({"error": "Coupon not found."}, status=status.HTTP_404_NOT_FOUND)

        if not coupon.is_available:
            return Response(
                {"error": "Coupon is not available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    with transaction.atomic():
        subtotal_amount = sum(item.subtotal for item in cart_items)
        discount_amount = 0
        if coupon:
            discount_amount = min(coupon.discount_amount, subtotal_amount)
        total_amount = subtotal_amount - discount_amount
        order = Order.objects.create(
            order_no=build_order_no(),
            user=user,
            merchant=merchant,
            delivery_type=delivery_type,
            subtotal_amount=subtotal_amount,
            discount_amount=discount_amount,
            coupon=coupon,
            total_amount=total_amount,
            status=Order.Status.PENDING_PAYMENT,
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                dish=item.dish,
                dish_name=item.dish.name,
                dish_price=item.unit_price,
                customization=item.customization,
                customization_label=item.customization_label,
                quantity=item.quantity,
                subtotal=item.subtotal,
            )
        if coupon:
            coupon.is_active = False
            coupon.used_at = timezone.now()
            coupon.save(update_fields=["is_active", "used_at"])
        cart_items.delete()

    order = (
        Order.objects.select_related("user", "merchant", "driver")
        .prefetch_related("items")
        .get(pk=order.pk)
    )
    return Response({"order": OrderSerializer(order).data}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def order_detail_view(request, pk):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    order = get_order_for_user(pk, user)
    if not order:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"order": OrderSerializer(order).data})


@api_view(["POST"])
def order_complete_view(request, pk):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    order = get_order_for_user(pk, user)
    if not order:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    allowed_statuses = {Order.Status.WAITING_PICKUP, Order.Status.DELIVERING}
    if order.status not in allowed_statuses:
        return Response(
            {"error": "Only waiting_pickup or delivering orders can be completed by customer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order.status = Order.Status.COMPLETED
    order.save(update_fields=["status"])
    return Response({"order": OrderSerializer(order).data})
