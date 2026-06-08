from django.conf import settings
from django.db import models

from dishes.models import Dish
from users.models import Coupon


class Order(models.Model):
    class DeliveryType(models.TextChoices):
        SELF_PICKUP = "self_pickup", "Self pickup"
        DELIVERY = "delivery", "Delivery"

    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PAID = "paid", "Paid"
        PREPARING = "preparing", "Preparing"
        WAITING_PICKUP = "waiting_pickup", "Waiting pickup"
        WAITING_DELIVERY = "waiting_delivery", "Waiting delivery"
        DELIVERING = "delivering", "Delivering"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    order_no = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="merchant_orders",
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_orders",
    )
    delivery_type = models.CharField(
        max_length=20,
        choices=DeliveryType.choices,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.order_no} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    dish_name = models.CharField(max_length=100)
    dish_price = models.DecimalField(max_digits=10, decimal_places=2)
    customization = models.JSONField(default=dict, blank=True)
    customization_label = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.dish_id and not self.dish_name:
            self.dish_name = self.dish.name
        if self.dish_id and self.dish_price is None:
            self.dish_price = self.dish.price
        self.subtotal = self.dish_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        suffix = f" ({self.customization_label})" if self.customization_label else ""
        return f"{self.order.order_no} - {self.dish_name}{suffix} x {self.quantity}"
