from django.urls import path

from . import views

urlpatterns = [
    path("dishes/", views.dish_list_view, name="dish-list"),
    path("dishes/<int:pk>/", views.dish_detail_view, name="dish-detail"),
]
