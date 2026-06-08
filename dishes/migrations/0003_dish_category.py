from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dishes", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="dish",
            name="category",
            field=models.CharField(
                choices=[
                    ("coffee", "Coffee"),
                    ("tea", "Tea"),
                    ("dessert", "Dessert"),
                    ("food", "Food"),
                ],
                default="coffee",
                max_length=20,
            ),
        ),
    ]
