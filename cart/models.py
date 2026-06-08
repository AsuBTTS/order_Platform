from django.conf import settings
from django.db import models

from dishes.models import Dish


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    customization = models.JSONField(default=dict, blank=True)
    customization_key = models.CharField(max_length=120, blank=True)
    customization_label = models.CharField(max_length=255, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    customization_price_delta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "dish", "customization_key"),
                name="unique_cart_item_per_user_dish_customization",
            )
        ]

    def save(self, *args, **kwargs):
        if self.dish_id and self.unit_price <= 0:
            self.unit_price = self.dish.price + self.customization_price_delta
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        suffix = f" ({self.customization_label})" if self.customization_label else ""
        return f"{self.user.username} - {self.dish.name}{suffix} x {self.quantity}"
