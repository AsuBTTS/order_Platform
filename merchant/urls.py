from django.urls import path

from . import views

urlpatterns = [
    path("merchant/dishes/", views.merchant_dishes_view, name="merchant-dishes"),
    path("merchant/dishes/create/", views.merchant_create_dish_view, name="merchant-dish-create"),
    path("merchant/dishes/<int:pk>/restock/", views.merchant_restock_dish_view, name="merchant-dish-restock"),
    path("merchant/orders/", views.merchant_orders_view, name="merchant-orders"),
    path("merchant/orders/<int:pk>/accept/", views.merchant_accept_order_view, name="merchant-order-accept"),
    path("merchant/orders/<int:pk>/finish/", views.merchant_finish_order_view, name="merchant-order-finish"),
]
