from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_coupon"),
    ]

    operations = [
        migrations.AddField(
            model_name="coupon",
            name="used_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
