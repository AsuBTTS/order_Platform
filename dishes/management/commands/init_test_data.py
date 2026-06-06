from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from dishes.models import Dish


class Command(BaseCommand):
    help = "Create or update initial test users and dishes for the ordering MVP."

    def handle(self, *args, **options):
        User = get_user_model()

        users = [
            {"username": "customer", "role": "customer", "phone": "13800000001"},
            {"username": "merchant", "role": "merchant", "phone": "13800000002"},
            {"username": "driver", "role": "driver", "phone": "13800000003"},
        ]

        for user_data in users:
            user, _ = User.objects.update_or_create(
                username=user_data["username"],
                defaults={
                    "role": user_data["role"],
                    "phone": user_data["phone"],
                    "is_active": True,
                },
            )
            user.set_password("123456")
            user.save(update_fields=["password", "role", "phone", "is_active"])

        merchant = User.objects.get(username="merchant")

        dishes = [
            {
                "name": "Classic Beef Burger",
                "price": Decimal("28.00"),
                "description": "Beef patty with lettuce, tomato, and cheese.",
                "stock": 50,
                "image": "images/classic-beef-burger.jpg",
                "status": Dish.Status.AVAILABLE,
            },
            {
                "name": "Chicken Rice Bowl",
                "price": Decimal("24.00"),
                "description": "Grilled chicken served with rice and vegetables.",
                "stock": 60,
                "image": "images/chicken-rice-bowl.jpg",
                "status": Dish.Status.AVAILABLE,
            },
            {
                "name": "Tomato Pasta",
                "price": Decimal("22.50"),
                "description": "Pasta with tomato sauce and herbs.",
                "stock": 40,
                "image": "images/tomato-pasta.jpg",
                "status": Dish.Status.AVAILABLE,
            },
            {
                "name": "Spicy Noodle Soup",
                "price": Decimal("19.90"),
                "description": "Warm noodle soup with a spicy broth.",
                "stock": 45,
                "image": "images/spicy-noodle-soup.jpg",
                "status": Dish.Status.AVAILABLE,
            },
            {
                "name": "Fruit Tea",
                "price": Decimal("12.00"),
                "description": "Refreshing mixed fruit tea.",
                "stock": 80,
                "image": "images/fruit-tea.jpg",
                "status": Dish.Status.AVAILABLE,
            },
            {
                "name": "Chocolate Cake",
                "price": Decimal("16.00"),
                "description": "Soft chocolate cake with cream.",
                "stock": 30,
                "image": "images/chocolate-cake.jpg",
                "status": Dish.Status.AVAILABLE,
            },
        ]

        for dish_data in dishes:
            Dish.objects.update_or_create(
                name=dish_data["name"],
                merchant=merchant,
                defaults=dish_data,
            )

        self.stdout.write(self.style.SUCCESS("Initial test data is ready."))
