from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_order_coupon_discount"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="customization",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="customization_label",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
