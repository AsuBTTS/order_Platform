from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "dish",
            "dish_name",
            "dish_price",
            "customization",
            "customization_label",
            "quantity",
            "subtotal",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_username = serializers.CharField(source="user.username", read_only=True)
    merchant_username = serializers.CharField(source="merchant.username", read_only=True)
    merchant_store_name = serializers.CharField(source="merchant.store_name", read_only=True)
    merchant_store_address = serializers.CharField(source="merchant.store_address", read_only=True)
    driver_username = serializers.CharField(source="driver.username", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_no",
            "user",
            "customer_username",
            "merchant",
            "merchant_username",
            "merchant_store_name",
            "merchant_store_address",
            "driver",
            "driver_username",
            "delivery_type",
            "subtotal_amount",
            "discount_amount",
            "coupon",
            "total_amount",
            "status",
            "created_at",
            "items",
        )
        read_only_fields = fields
