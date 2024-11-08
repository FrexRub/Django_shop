# Generated by Django 5.1.2 on 2024-10-31 13:17

import django.contrib.postgres.indexes
import django.core.validators
import myauth.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myauth", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=myauth.models.user_directory_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=("png", "jpg", "jpeg", "gif")
                    ),
                    myauth.models.validate_file_size,
                ],
                verbose_name="Аватар",
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="phone_number",
            field=models.CharField(
                max_length=15,
                validators=[
                    django.core.validators.RegexValidator(
                        "^((8|\\+7)[\\- ]?)?(\\(?\\d{3}\\)?[\\- ]?)?[\\d\\- ]{7,10}$"
                    )
                ],
                verbose_name="Телефон",
            ),
        ),
        migrations.AddIndex(
            model_name="profile",
            index=django.contrib.postgres.indexes.HashIndex(
                fields=["phone_number"], name="phone_hash_index"
            ),
        ),
    ]