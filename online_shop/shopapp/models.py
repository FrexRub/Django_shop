from django.db import models
from django.contrib.postgres.indexes import HashIndex
from django.core.validators import FileExtensionValidator
from django.urls import reverse

from services.utils import unique_slugify, validate_file_size


# Create your models here.
class Tag(models.Model):
    name = models.CharField(
        max_length=20,
        null=False,
    )

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


def category_directory_path(instance, filename):
    return "categories/category_{pk}/{filename}".format(pk=instance.id, filename=filename)


class Category(models.Model):
    title = models.CharField(
        max_length=30,
        null=False,
    )
    image = models.ImageField(
        verbose_name="category",
        null=True,
        blank=True,
        upload_to=category_directory_path,
        validators=[
            FileExtensionValidator(allowed_extensions=("png", "jpg", "jpeg", "gif")),
            validate_file_size,
        ],
    )
    slug = models.SlugField(verbose_name="URL", max_length=255, blank=True, unique=True)

    class Meta:
        """
        Сортировка, имена в административной панели, индексы
        """
        ordering = ("title",)
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
