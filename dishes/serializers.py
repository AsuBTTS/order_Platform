from rest_framework import serializers

from .models import Dish


class DishSerializer(serializers.ModelSerializer):
    merchant_username = serializers.CharField(source="merchant.username", read_only=True)
    merchant_store_name = serializers.CharField(source="merchant.store_name", read_only=True)
    merchant_store_address = serializers.CharField(source="merchant.store_address", read_only=True)

    class Meta:
        model = Dish
        fields = (
            "id",
            "name",
            "category",
            "price",
            "description",
            "stock",
            "merchant",
            "merchant_username",
            "merchant_store_name",
            "merchant_store_address",
            "image",
            "status",
        )
        read_only_fields = fields
