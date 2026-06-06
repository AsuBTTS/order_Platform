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
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "dish"),
                name="unique_cart_item_per_user_dish",
            )
        ]

    def save(self, *args, **kwargs):
        self.subtotal = self.dish.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.dish.name} x {self.quantity}"
