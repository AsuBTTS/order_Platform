from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from dishes.models import Dish


class Command(BaseCommand):
    help = "Create or update initial test users, stores, and dishes for the ordering MVP."

    def handle(self, *args, **options):
        User = get_user_model()

        users = [
            {"username": "customer", "role": "customer", "phone": "13800000001"},
            {"username": "driver", "role": "driver", "phone": "13800000003"},
            {
                "username": "admin",
                "role": "customer",
                "phone": "13800000004",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "merchant",
                "role": "merchant",
                "phone": "13800000002",
                "store_name": "花神咖啡馆·校园店",
                "store_address": "北京市海淀区学院路 88 号校园生活广场 1 层",
                "store_latitude": Decimal("39.992500"),
                "store_longitude": Decimal("116.337500"),
            },
            {
                "username": "merchant_west",
                "role": "merchant",
                "phone": "13800000005",
                "store_name": "花神咖啡馆·西小口店",
                "store_address": "北京市海淀区西小口路 18 号咖啡街区",
                "store_latitude": Decimal("40.052900"),
                "store_longitude": Decimal("116.351300"),
            },
            {
                "username": "merchant_tech",
                "role": "merchant",
                "phone": "13800000006",
                "store_name": "花神咖啡馆·东升科技园店",
                "store_address": "北京市海淀区东升科技园北街 6 号",
                "store_latitude": Decimal("40.035600"),
                "store_longitude": Decimal("116.332800"),
            },
        ]

        for user_data in users:
            store_defaults = {
                "store_name": user_data.get("store_name", ""),
                "store_address": user_data.get("store_address", ""),
                "store_latitude": user_data.get("store_latitude"),
                "store_longitude": user_data.get("store_longitude"),
            }
            user, _ = User.objects.update_or_create(
                username=user_data["username"],
                defaults={
                    "role": user_data["role"],
                    "phone": user_data["phone"],
                    "is_active": True,
                    "is_staff": user_data.get("is_staff", False),
                    "is_superuser": user_data.get("is_superuser", False),
                    **store_defaults,
                },
            )
            user.set_password("123456")
            user.save(
                update_fields=[
                    "password",
                    "role",
                    "phone",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "store_name",
                    "store_address",
                    "store_latitude",
                    "store_longitude",
                ]
            )

        store_dishes = {
            "merchant": [
                ("花神拿铁", Dish.Category.COFFEE, "28.00", "浓缩咖啡融合顺滑牛奶，口感温柔均衡。", 50),
                ("桂花美式", Dish.Category.COFFEE, "24.00", "清爽美式加入桂花香气，适合午后提神。", 60),
                ("白桃乌龙茶", Dish.Category.TEA, "22.00", "白桃果香与乌龙茶底，清甜不腻。", 80),
                ("海盐芝士蛋糕", Dish.Category.DESSERT, "26.00", "芝士香浓，海盐平衡甜度。", 24),
            ],
            "merchant_west": [
                ("燕麦焦糖拿铁", Dish.Category.COFFEE, "31.00", "燕麦奶与焦糖香气交织，甜度轻盈。", 42),
                ("冷萃咖啡", Dish.Category.COFFEE, "26.00", "低温慢萃，风味干净，带轻微果酸。", 45),
                ("茉莉柠檬茶", Dish.Category.TEA, "20.00", "茉莉茶香搭配新鲜柠檬，清爽明亮。", 30),
                ("伯爵红茶司康", Dish.Category.DESSERT, "18.00", "红茶香气明显，适合搭配拿铁。", 36),
            ],
            "merchant_tech": [
                ("抹茶云朵拿铁", Dish.Category.TEA, "30.00", "抹茶与奶泡层次丰富，入口绵密。", 35),
                ("莓果气泡茶", Dish.Category.TEA, "25.00", "莓果酸甜与气泡口感，适合夏日外送。", 48),
                ("可颂三明治", Dish.Category.FOOD, "32.00", "黄油可颂夹入火腿、芝士与生菜。", 28),
                ("花园沙拉碗", Dish.Category.FOOD, "29.00", "轻食蔬菜、鸡蛋与坚果，适合工作日午餐。", 32),
            ],
        }

        merchant_accounts = User.objects.filter(username__in=store_dishes.keys())
        Dish.objects.filter(merchant__in=merchant_accounts).update(status=Dish.Status.OFF_SHELF)

        for merchant_username, dishes in store_dishes.items():
            merchant = User.objects.get(username=merchant_username)
            for name, category, price, description, stock in dishes:
                Dish.objects.update_or_create(
                    name=name,
                    merchant=merchant,
                    defaults={
                        "category": category,
                        "price": Decimal(price),
                        "description": description,
                        "stock": stock,
                        "image": "",
                        "status": Dish.Status.AVAILABLE,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Initial test data is ready."))
