from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from dishes.models import Dish
from dishes.serializers import DishSerializer
from orders.models import Order
from orders.serializers import OrderSerializer
from users.models import User
from users.views import get_user_by_request


def require_merchant(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return None, error_response
    if user.role != User.Role.MERCHANT:
        return None, Response(
            {"error": "Only merchant users can perform this operation."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return user, None


def get_merchant_order(pk, merchant):
    try:
        return (
            Order.objects.select_related("user", "merchant", "driver")
            .prefetch_related("items")
            .get(pk=pk, merchant=merchant)
        )
    except Order.DoesNotExist:
        return None


@api_view(["GET"])
def merchant_orders_view(request):
    merchant, error_response = require_merchant(request)
    if error_response is not None:
        return error_response

    orders = (
        Order.objects.filter(merchant=merchant)
        .exclude(status=Order.Status.PENDING_PAYMENT)
        .select_related("user", "merchant", "driver")
        .prefetch_related("items")
    )
    return Response({"orders": OrderSerializer(orders, many=True).data})


@api_view(["GET"])
def merchant_dishes_view(request):
    merchant, error_response = require_merchant(request)
    if error_response is not None:
        return error_response

    dishes = Dish.objects.filter(merchant=merchant).order_by("id")
    return Response({"dishes": DishSerializer(dishes, many=True).data})


@api_view(["POST"])
def merchant_create_dish_view(request):
    merchant, error_response = require_merchant(request)
    if error_response is not None:
        return error_response

    name = str(request.data.get("name", "")).strip()
    description = str(request.data.get("description", "")).strip()
    category = request.data.get("category") or Dish.Category.COFFEE
    if not name:
        return Response({"error": "name is required."}, status=status.HTTP_400_BAD_REQUEST)
    if category not in Dish.Category.values:
        return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        price = float(request.data.get("price", 0))
        stock = int(request.data.get("stock", 0))
    except (TypeError, ValueError):
        return Response({"error": "price and stock must be numbers."}, status=status.HTTP_400_BAD_REQUEST)
    if price <= 0 or stock < 0:
        return Response({"error": "price must be greater than 0 and stock cannot be negative."}, status=status.HTTP_400_BAD_REQUEST)

    dish = Dish.objects.create(
        merchant=merchant,
        name=name,
        category=category,
        description=description,
        price=price,
        stock=stock,
        status=Dish.Status.AVAILABLE if stock > 0 else Dish.Status.SOLD_OUT,
    )
    return Response({"dish": DishSerializer(dish).data}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def merchant_restock_dish_view(request, pk):
    merchant, error_response = require_merchant(request)
    if error_response is not None:
        return error_response

    try:
        dish = Dish.objects.get(pk=pk, merchant=merchant)
    except Dish.DoesNotExist:
        return Response({"error": "Dish not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        quantity = int(request.data.get("quantity", 0))
    except (TypeError, ValueError):
        return Response(
            {"error": "quantity must be an integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity <= 0:
        return Response(
            {"error": "quantity must be greater than 0."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    dish.stock += quantity
    if dish.stock > 0 and dish.status == Dish.Status.SOLD_OUT:
        dish.status = Dish.Status.AVAILABLE
    dish.save(update_fields=["stock", "status"])
    return Response({"dish": DishSerializer(dish).data})


@api_view(["POST"])
def merchant_accept_order_view(request, pk):
    merchant, error_response = require_merchant(request)
    if error_response is not None:
        return error_response

    order = get_merchant_order(pk, merchant)
    if not order:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.Status.PAID:
        return Response(
            {"error": "Only paid orders can be accepted."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order.status = Order.Status.PREPARING
    order.save(update_fields=["status"])
    return Response({"order": OrderSerializer(order).data})


@api_view(["POST"])
def merchant_finish_order_view(request, pk):
    merchant, error_response = require_merchant(request)
    if error_response is not None:
        return error_response

    order = get_merchant_order(pk, merchant)
    if not order:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.Status.PREPARING:
        return Response(
            {"error": "Only preparing orders can be finished."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if order.delivery_type == Order.DeliveryType.SELF_PICKUP:
        order.status = Order.Status.WAITING_PICKUP
    else:
        order.status = Order.Status.WAITING_DELIVERY
    order.save(update_fields=["status"])
    return Response({"order": OrderSerializer(order).data})
