from django.urls import path

from . import views

urlpatterns = [
    path("payments/", views.payments_view, name="payments"),
    path("payments/<int:pk>/success/", views.payment_success_view, name="payment-success"),
    path("payments/<int:pk>/fail/", views.payment_fail_view, name="payment-fail"),
]
