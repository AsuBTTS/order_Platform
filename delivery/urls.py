from django.urls import path

from . import views

urlpatterns = [
    path("delivery/orders/", views.delivery_orders_view, name="delivery-orders"),
    path("delivery/orders/<int:pk>/accept/", views.delivery_accept_order_view, name="delivery-order-accept"),
    path("delivery/orders/<int:pk>/pickup/", views.delivery_pickup_order_view, name="delivery-order-pickup"),
    path("delivery/orders/<int:pk>/delivered/", views.delivery_delivered_order_view, name="delivery-order-delivered"),
]
