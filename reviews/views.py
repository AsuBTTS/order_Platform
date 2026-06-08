from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from orders.models import Order
from users.views import get_user_by_request

from .models import Review
from .serializers import ReviewSerializer


@api_view(["POST"])
def reviews_view(request):
    user, error_response = get_user_by_request(request)
    if error_response is not None:
        return error_response

    order_id = request.data.get("order_id")
    score = request.data.get("score")
    content = request.data.get("content", "")

    try:
        order = Order.objects.get(pk=order_id, user=user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.Status.COMPLETED:
        return Response(
            {"error": "Only completed orders can be reviewed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if Review.objects.filter(order=order).exists():
        return Response(
            {"error": "This order has already been reviewed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        score = int(score)
    except (TypeError, ValueError):
        return Response(
            {"error": "score must be an integer from 1 to 5."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if score < 1 or score > 5:
        return Response(
            {"error": "score must be an integer from 1 to 5."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    review = Review.objects.create(order=order, user=user, score=score, content=content)
    return Response({"review": ReviewSerializer(review).data}, status=status.HTTP_201_CREATED)
