from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from dishes.models import Dish
from dishes.serializers import DishSerializer
from orders.models import Order
from orders.serializers import OrderSerializer

from .models import Coupon
from .serializers import CouponSerializer, UserSerializer


def get_user_by_request(request):
    user_id = request.data.get("user_id") or request.query_params.get("user_id")
    if not user_id:
        return None, Response(
            {"error": "user_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    User = get_user_model()
    try:
        return User.objects.get(id=user_id), None
    except User.DoesNotExist:
        return None, Response(
            {"error": "User not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
def register_view(request):
    username = str(request.data.get("username", "")).strip()
    password = str(request.data.get("password", ""))
    phone = str(request.data.get("phone", "")).strip()

    if not username or not password:
        return Response(
            {"error": "username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(password) < 6:
        return Response(
            {"error": "password must be at least 6 characters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create(
        username=username,
        phone=phone,
        role=User.Role.CUSTOMER,
        is_active=True,
    )
    user.set_password(password)
    user.save(update_fields=["password"])
    return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.check_password(password):
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.is_active:
        return Response(
            {"error": "This user has been disabled by platform admin."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response({"user": UserSerializer(user).data})


@api_view(["GET"])
def current_user_view(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    return Response({"user": UserSerializer(user).data})


@api_view(["GET"])
def store_list_view(request):
    User = get_user_model()
    stores = (
        User.objects.filter(role=User.Role.MERCHANT, is_active=True)
        .exclude(store_latitude__isnull=True)
        .exclude(store_longitude__isnull=True)
        .order_by("id")
    )
    return Response({"stores": UserSerializer(stores, many=True).data})


@api_view(["POST"])
def change_password_view(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    if not old_password or not new_password:
        return Response(
            {"error": "old_password and new_password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
    if len(str(new_password)) < 6:
        return Response({"error": "new_password must be at least 6 characters."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save(update_fields=["password"])
    return Response({"message": "Password updated successfully."})


@api_view(["POST"])
def update_profile_view(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    username = str(request.data.get("username", "")).strip()
    phone = str(request.data.get("phone", "")).strip()

    if not username:
        return Response({"error": "username is required."}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    if User.objects.exclude(pk=user.pk).filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    user.username = username
    user.phone = phone
    user.save(update_fields=["username", "phone"])
    return Response({"user": UserSerializer(user).data})


def require_platform_admin(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return None, error_response
    if not (user.is_staff or user.is_superuser):
        return None, Response(
            {"error": "Only platform admin users can perform this operation."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return user, None


@api_view(["GET"])
def platform_dashboard_view(request):
    _, error_response = require_platform_admin(request)
    if error_response is not None:
        return error_response

    User = get_user_model()
    active_order_statuses = [
        Order.Status.PAID,
        Order.Status.PREPARING,
        Order.Status.WAITING_PICKUP,
        Order.Status.WAITING_DELIVERY,
        Order.Status.DELIVERING,
        Order.Status.COMPLETED,
    ]
    revenue = (
        Order.objects.filter(status__in=active_order_statuses)
        .aggregate(total=Sum("total_amount"))
        .get("total")
        or 0
    )
    role_counts = {
        row["role"]: row["count"]
        for row in User.objects.values("role").annotate(count=Count("id"))
    }
    status_counts = {
        row["status"]: row["count"]
        for row in Order.objects.values("status").annotate(count=Count("id"))
    }
    recent_orders = (
        Order.objects.select_related("user", "merchant", "driver")
        .prefetch_related("items")
        .order_by("-created_at")[:8]
    )

    return Response(
        {
            "metrics": {
                "users": User.objects.count(),
                "disabled_users": User.objects.filter(is_active=False).count(),
                "merchants": role_counts.get("merchant", 0),
                "drivers": role_counts.get("driver", 0),
                "dishes": Dish.objects.count(),
                "orders": Order.objects.count(),
                "coupons": Coupon.objects.count(),
                "revenue": str(revenue),
            },
            "role_counts": role_counts,
            "status_counts": status_counts,
            "recent_orders": OrderSerializer(recent_orders, many=True).data,
        }
    )


@api_view(["GET"])
def platform_users_view(request):
    _, error_response = require_platform_admin(request)
    if error_response is not None:
        return error_response

    User = get_user_model()
    users = User.objects.order_by("id")
    role = request.query_params.get("role")
    query = str(request.query_params.get("q", "")).strip()
    if role:
        users = users.filter(role=role)
    if query:
        users = users.filter(username__icontains=query)
    return Response({"users": UserSerializer(users, many=True).data})


@api_view(["POST"])
def platform_user_status_view(request, pk):
    admin, error_response = require_platform_admin(request)
    if error_response is not None:
        return error_response

    User = get_user_model()
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    if user.id == admin.id and request.data.get("is_active") is False:
        return Response(
            {"error": "Platform admin cannot disable the current account."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    is_active = request.data.get("is_active")
    if not isinstance(is_active, bool):
        return Response(
            {"error": "is_active must be true or false."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.is_active = is_active
    user.save(update_fields=["is_active"])
    return Response({"user": UserSerializer(user).data})


@api_view(["GET", "POST"])
def platform_coupons_view(request):
    admin, error_response = require_platform_admin(request)
    if error_response is not None:
        return error_response

    if request.method == "GET":
        coupons = Coupon.objects.select_related("issued_to", "created_by").order_by("-created_at")
        return Response({"coupons": CouponSerializer(coupons, many=True).data})

    User = get_user_model()
    target_user_id = request.data.get("issued_to")
    try:
        target_user = User.objects.get(pk=target_user_id)
    except User.DoesNotExist:
        return Response({"error": "Target user not found."}, status=status.HTTP_404_NOT_FOUND)

    if target_user.role != User.Role.CUSTOMER:
        return Response(
            {"error": "Coupons can only be issued to customer users."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    title = str(request.data.get("title", "")).strip()
    if not title:
        return Response({"error": "title is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        discount_amount = float(request.data.get("discount_amount", 0))
    except (TypeError, ValueError):
        return Response({"error": "discount_amount must be a number."}, status=status.HTTP_400_BAD_REQUEST)

    if discount_amount <= 0:
        return Response({"error": "discount_amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

    code = str(request.data.get("code", "")).strip().upper()
    if not code:
        code = f"FL{get_random_string(8).upper()}"

    coupon = Coupon.objects.create(
        code=code,
        title=title,
        description=str(request.data.get("description", "")).strip(),
        discount_amount=discount_amount,
        issued_to=target_user,
        created_by=admin,
        valid_until=request.data.get("valid_until") or None,
        is_active=True,
    )
    return Response({"coupon": CouponSerializer(coupon).data}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def user_coupons_view(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    coupons = Coupon.objects.filter(issued_to=user).select_related("issued_to", "created_by")
    return Response({"coupons": CouponSerializer(coupons, many=True).data})


@api_view(["GET"])
def platform_dishes_view(request):
    _, error_response = require_platform_admin(request)
    if error_response is not None:
        return error_response

    dishes = Dish.objects.select_related("merchant").order_by("id")
    query = str(request.query_params.get("q", "")).strip()
    if query:
        dishes = dishes.filter(name__icontains=query)
    return Response({"dishes": DishSerializer(dishes, many=True).data})


@api_view(["POST"])
def platform_dish_create_view(request):
    _, error_response = require_platform_admin(request)
    if error_response is not None:
        return error_response

    User = get_user_model()
    merchant_id = request.data.get("merchant")
    try:
        merchant = User.objects.get(pk=merchant_id, role=User.Role.MERCHANT)
    except User.DoesNotExist:
        return Response({"error": "Merchant account not found."}, status=status.HTTP_404_NOT_FOUND)

    name = str(request.data.get("name", "")).strip()
    description = str(request.data.get("description", "")).strip()
    category = request.data.get("category") or Dish.Category.COFFEE
    status_value = request.data.get("status") or Dish.Status.AVAILABLE
    if not name:
        return Response({"error": "name is required."}, status=status.HTTP_400_BAD_REQUEST)
    if category not in Dish.Category.values:
        return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)
    if status_value not in Dish.Status.values:
        return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        price = Decimal(str(request.data.get("price", "0")))
        stock = int(request.data.get("stock", 0))
    except (TypeError, ValueError, ArithmeticError):
        return Response({"error": "price and stock must be valid numbers."}, status=status.HTTP_400_BAD_REQUEST)
    if price <= 0 or stock < 0:
        return Response({"error": "price must be greater than 0 and stock cannot be negative."}, status=status.HTTP_400_BAD_REQUEST)

    dish = Dish.objects.create(
        merchant=merchant,
        name=name,
        category=category,
        price=price,
        description=description,
        stock=stock,
        status=status_value,
    )
    return Response({"dish": DishSerializer(dish).data}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def platform_dish_update_view(request, pk):
    _, error_response = require_platform_admin(request)
    if error_response is not None:
        return error_response

    try:
        dish = Dish.objects.get(pk=pk)
    except Dish.DoesNotExist:
        return Response({"error": "Dish not found."}, status=status.HTTP_404_NOT_FOUND)

    update_fields = []
    if "status" in request.data:
        if request.data["status"] not in Dish.Status.values:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        dish.status = request.data["status"]
        update_fields.append("status")
    if "category" in request.data:
        if request.data["category"] not in Dish.Category.values:
            return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)
        dish.category = request.data["category"]
        update_fields.append("category")
    if "price" in request.data:
        try:
            price = float(request.data["price"])
        except (TypeError, ValueError):
            return Response({"error": "price must be a number."}, status=status.HTTP_400_BAD_REQUEST)
        if price <= 0:
            return Response({"error": "price must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        dish.price = price
        update_fields.append("price")

    if update_fields:
        dish.save(update_fields=update_fields)
    return Response({"dish": DishSerializer(dish).data})


@api_view(["POST"])
def platform_store_account_view(request):
    _, error_response = require_platform_admin(request)
    if error_response is not None:
        return error_response

    User = get_user_model()
    target_user_id = request.data.get("target_user_id")
    username = str(request.data.get("username", "")).strip()
    password = str(request.data.get("password", "")).strip()
    phone = str(request.data.get("phone", "")).strip()

    if target_user_id:
        try:
            user = User.objects.get(pk=target_user_id)
        except User.DoesNotExist:
            return Response({"error": "Target user not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        if not username:
            return Response({"error": "username is required."}, status=status.HTTP_400_BAD_REQUEST)
        user, created = User.objects.get_or_create(username=username)
        if created and not password:
            password = "123456"

    if username and User.objects.exclude(pk=user.pk).filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    store_name = str(request.data.get("store_name", "")).strip()
    store_address = str(request.data.get("store_address", "")).strip()
    if not store_name or not store_address:
        return Response({"error": "store_name and store_address are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        store_latitude = Decimal(str(request.data.get("store_latitude")))
        store_longitude = Decimal(str(request.data.get("store_longitude")))
    except (TypeError, ArithmeticError):
        return Response({"error": "store_latitude and store_longitude must be valid numbers."}, status=status.HTTP_400_BAD_REQUEST)

    user.username = username or user.username
    user.phone = phone
    user.role = User.Role.MERCHANT
    user.store_name = store_name
    user.store_address = store_address
    user.store_latitude = store_latitude
    user.store_longitude = store_longitude
    user.is_active = True
    if password:
        if len(password) < 6:
            return Response({"error": "password must be at least 6 characters."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
    user.save()
    return Response({"user": UserSerializer(user).data})
