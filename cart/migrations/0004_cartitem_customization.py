from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0003_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="cartitem",
            name="unique_cart_item_per_user_dish",
        ),
        migrations.AddField(
            model_name="cartitem",
            name="customization",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="customization_key",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="customization_label",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="customization_price_delta",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="unit_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddConstraint(
            model_name="cartitem",
            constraint=models.UniqueConstraint(
                fields=("user", "dish", "customization_key"),
                name="unique_cart_item_per_user_dish_customization",
            ),
        ),
    ]
