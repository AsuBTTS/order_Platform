from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import OrderSerializer
from users.models import User
from users.views import get_user_by_request


def require_driver(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return None, error_response
    if user.role != User.Role.DRIVER:
        return None, Response(
            {"error": "Only driver users can perform this operation."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return user, None


@api_view(["GET"])
def delivery_orders_view(request):
    driver, error_response = require_driver(request)
    if error_response is not None:
        return error_response

    orders = (
        Order.objects.filter(status=Order.Status.WAITING_DELIVERY, driver__isnull=True)
        | Order.objects.filter(status=Order.Status.WAITING_DELIVERY, driver=driver)
        | Order.objects.filter(status=Order.Status.DELIVERING, driver=driver)
    )
    orders = orders.select_related("user", "merchant", "driver").prefetch_related("items")
    return Response({"orders": OrderSerializer(orders, many=True).data})


@api_view(["POST"])
def delivery_accept_order_view(request, pk):
    driver, error_response = require_driver(request)
    if error_response is not None:
        return error_response

    try:
        order = (
            Order.objects.select_related("user", "merchant", "driver")
            .prefetch_related("items")
            .get(pk=pk)
        )
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.Status.WAITING_DELIVERY:
        return Response(
            {"error": "Only waiting_delivery orders can be accepted."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if order.driver_id and order.driver_id != driver.id:
        return Response(
            {"error": "This order has already been accepted by another driver."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order.driver = driver
    order.save(update_fields=["driver"])
    return Response({"order": OrderSerializer(order).data})


@api_view(["POST"])
def delivery_pickup_order_view(request, pk):
    driver, error_response = require_driver(request)
    if error_response is not None:
        return error_response

    try:
        order = (
            Order.objects.select_related("user", "merchant", "driver")
            .prefetch_related("items")
            .get(pk=pk)
        )
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.Status.WAITING_DELIVERY:
        return Response(
            {"error": "Only waiting_delivery orders can be picked up."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if order.driver_id and order.driver_id != driver.id:
        return Response(
            {"error": "This order belongs to another driver."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order.driver = driver
    order.status = Order.Status.DELIVERING
    order.save(update_fields=["driver", "status"])
    return Response({"order": OrderSerializer(order).data})


@api_view(["POST"])
def delivery_delivered_order_view(request, pk):
    driver, error_response = require_driver(request)
    if error_response is not None:
        return error_response

    try:
        order = (
            Order.objects.select_related("user", "merchant", "driver")
            .prefetch_related("items")
            .get(pk=pk, driver=driver)
        )
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.Status.DELIVERING:
        return Response(
            {"error": "Only delivering orders can be marked as delivered."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order.status = Order.Status.COMPLETED
    order.save(update_fields=["status"])
    return Response({"order": OrderSerializer(order).data})
