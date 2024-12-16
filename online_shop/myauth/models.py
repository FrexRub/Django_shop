import os
from pathlib import Path
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.indexes import HashIndex
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.validators import RegexValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver


from services.utils import unique_slugify, validate_file_size

# BASE_DIR = Path(__file__).resolve().parent.parent
# MEDIA_ROOT = BASE_DIR / "upload"

phone_number_validator = RegexValidator(
    r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"
)

log = logging.getLogger(__name__)

def user_directory_path(instance, filename):
    return "profile/user_{pk}/{filename}".format(pk=instance.user.id, filename=filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(
        max_length=15, verbose_name="Телефон", validators=[phone_number_validator]
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        null=True,
        blank=True,
        upload_to=user_directory_path,
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
        ordering = ("user",)
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

        indexes = [
            HashIndex(fields=['phone_number'], name='phone_hash_index'),
        ]

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.user.username)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Возвращение строки
        """
        return self.user.username

    def get_absolute_url(self):
        """
        Ссылка на профиль
        """
        return reverse("profile_detail", kwargs={"slug": self.slug})

@receiver(pre_save, sender=Profile)
def delete_old_avatar(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_avatar = Profile.objects.get(pk=instance.pk).avatar
        except Profile.DoesNotExist:
            return
        # Если изображение изменено, удаляем старый файл
        if old_avatar and old_avatar != instance.avatar:
            print(old_avatar.path)

            if os.path.isfile(old_avatar.path):
                log.info("Старый аватар пользователя удален")
                os.remove(old_avatar.path)