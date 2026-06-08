from decimal import Decimal

from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from dishes.models import Dish
from users.views import get_user_by_request

from .models import CartItem
from .serializers import CartItemSerializer


CUSTOMIZATION_RULES = {
    "temperature": {
        "iced": ("Iced", Decimal("0.00")),
        "hot": ("Hot", Decimal("0.00")),
    },
    "ice": {
        "regular": ("Regular ice", Decimal("0.00")),
        "less": ("Less ice", Decimal("0.00")),
        "none": ("No ice", Decimal("0.00")),
    },
    "size": {
        "small": ("Small", Decimal("0.00")),
        "medium": ("Medium +3", Decimal("3.00")),
        "large": ("Large +5", Decimal("5.00")),
    },
}


def build_customization(raw_customization):
    raw_customization = raw_customization if isinstance(raw_customization, dict) else {}
    normalized = {
        "temperature": raw_customization.get("temperature") or "iced",
        "ice": raw_customization.get("ice") or "regular",
        "size": raw_customization.get("size") or "small",
    }

    labels = []
    price_delta = Decimal("0.00")
    for key, value in normalized.items():
        rule = CUSTOMIZATION_RULES[key]
        if value not in rule:
            raise ValueError(f"Invalid customization option: {key}.")
        label, delta = rule[value]
        labels.append(label)
        price_delta += delta

    customization_key = "|".join(f"{key}:{normalized[key]}" for key in ("temperature", "ice", "size"))
    return normalized, customization_key, " / ".join(labels), price_delta


def cart_response(user, response_status=status.HTTP_200_OK):
    items = CartItem.objects.filter(user=user).select_related("dish", "dish__merchant")
    total = items.aggregate(total=Sum("subtotal"))["total"] or 0
    return Response(
        {
            "items": CartItemSerializer(items, many=True).data,
            "total_amount": total,
        },
        status=response_status,
    )


@api_view(["GET", "POST"])
def cart_items_view(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    if request.method == "GET":
        return cart_response(user)

    dish_id = request.data.get("dish_id")
    try:
        quantity = int(request.data.get("quantity", 1))
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

    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return Response({"error": "Dish not found."}, status=status.HTTP_404_NOT_FOUND)

    merchant_id = request.data.get("merchant_id")
    if merchant_id and str(dish.merchant_id) != str(merchant_id):
        return Response(
            {"error": "Dish does not belong to the selected store."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    existing_items = CartItem.objects.filter(user=user).select_related("dish")
    if existing_items.exists() and any(item.dish.merchant_id != dish.merchant_id for item in existing_items):
        return Response(
            {"error": "Cart already contains dishes from another store. Please clear it before switching stores."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if dish.status != Dish.Status.AVAILABLE:
        return Response(
            {"error": "Dish is not available."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if dish.stock < quantity:
        return Response(
            {"error": "Dish stock is insufficient."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        customization, customization_key, customization_label, price_delta = build_customization(
            request.data.get("customization")
        )
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    item, created = CartItem.objects.get_or_create(
        user=user,
        dish=dish,
        customization_key=customization_key,
        defaults={
            "quantity": quantity,
            "customization": customization,
            "customization_label": customization_label,
            "customization_price_delta": price_delta,
            "unit_price": dish.price + price_delta,
        },
    )
    if not created:
        new_quantity = item.quantity + quantity
        if dish.stock < new_quantity:
            return Response(
                {"error": "Dish stock is insufficient."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.quantity = new_quantity
    item.save()

    return cart_response(user, status.HTTP_201_CREATED)


@api_view(["PUT", "DELETE"])
def cart_item_detail_view(request, pk):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    try:
        item = CartItem.objects.select_related("dish").get(pk=pk, user=user)
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Cart item not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "DELETE":
        item.delete()
        return cart_response(user)

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
    if item.dish.stock < quantity:
        return Response(
            {"error": "Dish stock is insufficient."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    item.quantity = quantity
    item.save()
    return cart_response(user)
