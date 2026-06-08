from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_no = serializers.CharField(source="order.order_no", read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "order", "order_no", "payment_type", "amount", "status", "paid_at")
        read_only_fields = fields
