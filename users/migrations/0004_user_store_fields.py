from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_coupon_used_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="store_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="user",
            name="store_address",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="user",
            name="store_latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="store_longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True),
        ),
    ]
