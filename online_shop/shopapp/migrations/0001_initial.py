# Generated by Django 5.1.2 on 2024-10-31 14:34

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20)),
            ],
            options={
                "verbose_name": "Тэг",
                "verbose_name_plural": "Тэги",
                "ordering": ("name",),
                "indexes": [
                    django.contrib.postgres.indexes.HashIndex(
                        fields=["name"], name="tag_hash_index"
                    )
                ],
            },
        ),
    ]
