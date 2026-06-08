from django.urls import path

from . import views

urlpatterns = [
    path("cart/items/", views.cart_items_view, name="cart-items"),
    path("cart/items/<int:pk>/", views.cart_item_detail_view, name="cart-item-detail"),
]
