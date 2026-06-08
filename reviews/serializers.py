from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    order_no = serializers.CharField(source="order.order_no", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "order", "order_no", "user", "username", "score", "content", "created_at")
        read_only_fields = fields
