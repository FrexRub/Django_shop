from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.indexes import HashIndex, BrinIndex
from django.core.validators import FileExtensionValidator
from django.urls import reverse

from services.utils import unique_slugify, validate_file_size


def category_directory_path(instance: "Category", filename: str) -> str:
    return "categories/category_{name}/{filename}".format(
        name=instance.title, filename=filename
    )


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/{filename}".format(
        pk=instance.product.id,
        filename=filename,
    )


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, null=False, verbose_name="Наименование тэга")

    class Meta:
        """
        Сортировка, имена в административной панели, индексы
        """

        ordering = ("name",)
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

        indexes = [
            HashIndex(fields=["name"], name="tag_hash_index"),
        ]

    def __str__(self):
        """
        Возвращение строки
        """
        return self.name


class Category(models.Model):
    title = models.CharField(
        max_length=100,
        null=False,
        verbose_name="Наименование",
    )
    image = models.ImageField(
        verbose_name="Изображение",
        null=True,
        blank=True,
        upload_to=category_directory_path,
        validators=[
            FileExtensionValidator(allowed_extensions=("png", "jpg", "jpeg", "gif")),
            validate_file_size,
        ],
    )
    subcategories = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="category",
        verbose_name="Наименование родительской категории",
    )
    tags = models.ManyToManyField(
        Tag, blank=True, verbose_name="Тэг", related_name="category"
    )
    slug = models.SlugField(verbose_name="URL", max_length=255, blank=True, unique=True)

    class Meta:
        """
        Сортировка, имена в административной панели, индексы
        """

        ordering = ("id",)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Возвращение строки
        """
        return self.title

    def get_absolute_url(self):
        """
        Ссылка на категорию
        """
        return reverse("category_detail", kwargs={"slug": self.slug})


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="Категория товара",
        related_name="products",
    )
    price = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Цена",
        db_index=True,
    )
    count = models.PositiveSmallIntegerField(
        default=0, verbose_name="Количество товара", db_index=True
    )
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(
        max_length=150, null=False, blank=True, verbose_name="Наименование"
    )
    description = models.CharField(
        max_length=250, null=False, blank=True, verbose_name="Описание"
    )
    fullDescription = models.TextField(
        null=False, blank=True, verbose_name="Полное описание"
    )
    freeDelivery = models.BooleanField(
        default=False, verbose_name="Бесплатная доставка"
    )
    tags = models.ManyToManyField(Tag, related_name="products", verbose_name="Тэг")

    slug = models.SlugField(verbose_name="URL", max_length=255, blank=True, unique=True)

    class Meta:
        """
        Сортировка, имена в административной панели, индексы
        """

        ordering = ("price",)
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

        indexes = [
            BrinIndex(fields=["date"], name="product_date_index"),
        ]

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Возвращение строки
        """
        return self.title

    def get_absolute_url(self):
        """
        Ссылка на категорию
        """
        return reverse("product_detail", kwargs={"slug": self.slug})


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    src = models.ImageField(upload_to=product_images_directory_path)
    alt = models.CharField(max_length=200, null=False, blank=True)

    class Meta:
        """
        Сортировка, имена в административной панели, индексы
        """

        ordering = ("id",)
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товара"

    def __str__(self):
        """
        Возвращение строки
        """
        return self.alt


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews", verbose_name="Автор"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Товар"
    )
    text = models.CharField(
        max_length=500, null=False, blank=True, verbose_name="Содержание"
    )
    rate = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка",
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Сортировка, имена в административной панели, индексы
        """

        ordering = ("-date",)
        verbose_name = "Отзыв о товаре"
        verbose_name_plural = "Отзывы о товаре"

        indexes = [
            BrinIndex(fields=["date"], name="review_date_index"),
        ]

    def __str__(self):
        """
        Возвращение строки
        """
        return f"{self.author.username}_{self.product.title}"


class Specification(models.Model):
    name = models.CharField(
        max_length=100, null=False, blank=True, verbose_name="Наименование"
    )
    value = models.CharField(
        max_length=150, null=False, blank=True, verbose_name="Значение"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications",
        verbose_name="Товар",
    )

    class Meta:
        """
        Сортировка, имена в административной панели, индексы
        """

        verbose_name = "Спецификация товара"
        verbose_name_plural = "Спецификации товаров"

    def __str__(self):
        """
        Возвращение строки
        """
        return f"{self.product.title}_{self.name}"


class Sales(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="sales",
        verbose_name="Товар",
    )
    salePrice = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Цена со скидкой",
    )

    dateFrom = models.DateTimeField(blank=True, verbose_name="Дата начала скидки")
    dateTo = models.DateTimeField(blank=True, verbose_name="Дата окончания скидки")

    class Meta:
        ordering = ("id",)
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"

    def __str__(self):
        """
        Возвращение строки
        """
        return f"Sale_{self.product.title}"
