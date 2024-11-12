# Generated by Django 5.1.2 on 2024-11-11 09:14

import django.contrib.postgres.indexes
import django.core.validators
import django.db.models.deletion
import services.utils
import shopapp.models
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0015_alter_tag_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={
                "ordering": ("id",),
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
            },
        ),
        migrations.AlterField(
            model_name="category",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=shopapp.models.category_directory_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=("png", "jpg", "jpeg", "gif")
                    ),
                    services.utils.validate_file_size,
                ],
                verbose_name="Изображение",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="subcategories",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="category",
                to="shopapp.category",
                verbose_name="Наименование родительской категории",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                null=True,
                related_name="category",
                to="shopapp.tag",
                verbose_name="Тэг",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="title",
            field=models.CharField(max_length=100, verbose_name="Наименование"),
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="shopapp.category",
                verbose_name="Категория товара",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="count",
            field=models.PositiveSmallIntegerField(
                db_index=True, default=0, verbose_name="Количество товара"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.CharField(blank=True, max_length=250, verbose_name="Описание"),
        ),
        migrations.AlterField(
            model_name="product",
            name="freeDelivery",
            field=models.BooleanField(
                default=False, verbose_name="Бесплатная доставка"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="fullDescription",
            field=models.TextField(blank=True, verbose_name="Полное описание"),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                db_index=True,
                decimal_places=2,
                default=0,
                max_digits=8,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                verbose_name="Цена",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="tags",
            field=models.ManyToManyField(
                related_name="products", to="shopapp.tag", verbose_name="Тэг"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="title",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="Наименование"
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="shopapp.product",
                verbose_name="Товар",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews",
                to="shopapp.product",
                verbose_name="Товар",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="rate",
            field=models.PositiveSmallIntegerField(
                default=1,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5),
                ],
                verbose_name="Оценка",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="text",
            field=models.CharField(
                blank=True, max_length=500, verbose_name="Содержание"
            ),
        ),
        migrations.AlterField(
            model_name="specification",
            name="name",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="Наименование"
            ),
        ),
        migrations.AlterField(
            model_name="specification",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="specifications",
                to="shopapp.product",
                verbose_name="Товар",
            ),
        ),
        migrations.AlterField(
            model_name="specification",
            name="value",
            field=models.CharField(blank=True, max_length=150, verbose_name="Значение"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=django.contrib.postgres.indexes.BrinIndex(
                fields=["date"], name="product_date_index"
            ),
        ),
        migrations.AddIndex(
            model_name="review",
            index=django.contrib.postgres.indexes.BrinIndex(
                fields=["date"], name="review_date_index"
            ),
        ),
    ]