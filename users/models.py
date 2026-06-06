from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        MERCHANT = "merchant", "Merchant"
        DRIVER = "driver", "Driver"

    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
