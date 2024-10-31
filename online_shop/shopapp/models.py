from django.db import models
from django.contrib.postgres.indexes import HashIndex


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
