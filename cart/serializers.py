from rest_framework import serializers

from dishes.serializers import DishSerializer

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "user",
            "dish",
            "customization",
            "customization_key",
            "customization_label",
            "unit_price",
            "customization_price_delta",
            "quantity",
            "subtotal",
        )
        read_only_fields = fields
