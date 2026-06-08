from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Dish
from .serializers import DishSerializer


@api_view(["GET"])
def dish_list_view(request):
    category = request.query_params.get("category")
    merchant_id = request.query_params.get("merchant_id")
    dishes = Dish.objects.select_related("merchant").filter(status=Dish.Status.AVAILABLE)
    if merchant_id:
        dishes = dishes.filter(merchant_id=merchant_id)
    if category:
        dishes = dishes.filter(category=category)
    dishes = dishes.order_by("id")
    return Response({"dishes": DishSerializer(dishes, many=True).data})


@api_view(["GET"])
def dish_detail_view(request, pk):
    try:
        dish = Dish.objects.select_related("merchant").get(pk=pk)
    except Dish.DoesNotExist:
        return Response({"error": "Dish not found."}, status=404)

    return Response({"dish": DishSerializer(dish).data})
