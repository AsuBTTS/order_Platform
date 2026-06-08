from rest_framework import serializers

from .models import Coupon, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "phone",
            "role",
            "store_name",
            "store_address",
            "store_latitude",
            "store_longitude",
            "is_active",
            "is_staff",
            "is_superuser",
        )
        read_only_fields = fields


class CouponSerializer(serializers.ModelSerializer):
    issued_to_username = serializers.CharField(source="issued_to.username", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = (
            "id",
            "code",
            "title",
            "description",
            "discount_amount",
            "issued_to",
            "issued_to_username",
            "created_by",
            "created_by_username",
            "valid_until",
            "is_active",
            "is_available",
            "used_at",
            "created_at",
        )
        read_only_fields = fields
