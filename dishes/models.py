from django.conf import settings
from django.db import models


class Dish(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        SOLD_OUT = "sold_out", "Sold out"
        OFF_SHELF = "off_shelf", "Off shelf"

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dishes",
    )
    image = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    def __str__(self):
        return f"{self.name} ({self.price})"
