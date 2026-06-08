from django.urls import path

from . import views

urlpatterns = [
    path("orders/", views.orders_view, name="orders"),
    path("orders/<int:pk>/", views.order_detail_view, name="order-detail"),
    path("orders/<int:pk>/complete/", views.order_complete_view, name="order-complete"),
]
