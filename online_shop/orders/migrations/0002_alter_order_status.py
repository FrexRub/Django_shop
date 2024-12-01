# Generated by Django 5.1.2 on 2024-11-30 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("created", "Created"),
                    ("accepted", "Accepted"),
                    ("paid", "Paid"),
                ],
                default="created",
                max_length=9,
                verbose_name="Статус заказа",
            ),
        ),
    ]