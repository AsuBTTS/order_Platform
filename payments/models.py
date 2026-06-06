from django.db import models
from django.utils import timezone

from orders.models import Order


class Payment(models.Model):
    class PaymentType(models.TextChoices):
        MOCK_WECHAT = "mock_wechat", "Mock WeChat"
        MOCK_ALIPAY = "mock_alipay", "Mock Alipay"
        MOCK_BALANCE = "mock_balance", "Mock balance"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    payment_type = models.CharField(
        max_length=30,
        choices=PaymentType.choices,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    def mark_success(self):
        self.status = self.Status.SUCCESS
        self.paid_at = timezone.now()

    def __str__(self):
        return f"{self.order.order_no} - {self.amount} ({self.status})"
