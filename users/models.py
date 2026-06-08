from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        MERCHANT = "merchant", "Merchant"
        DRIVER = "driver", "Driver"

    phone = models.CharField(max_length=20, blank=True)
    store_name = models.CharField(max_length=100, blank=True)
    store_address = models.CharField(max_length=255, blank=True)
    store_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    store_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class Coupon(models.Model):
    code = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coupons",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_coupons",
    )
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_available(self):
        if not self.is_active or self.used_at:
            return False
        if self.valid_until and self.valid_until < timezone.localdate():
            return False
        return True

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.code} - {self.title}"
