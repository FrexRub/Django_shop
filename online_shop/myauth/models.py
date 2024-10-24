from django.contrib.auth.models import User
from django.db import models
from django.core.validators import FileExtensionValidator
from django.urls import reverse

from services.utils import unique_slugify

def user_directory_path(instance, filename):
    return "user_{pk}/{filename}".format(pk=instance.user.id, filename=filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, verbose_name="Телефон")
    avatar = models.ImageField(
        verbose_name="Аватар",
        null=True,
        blank=True,
        upload_to=user_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=("png", "jpg", "jpeg"))],
    )
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)

    class Meta:
        """
        Сортировка, название таблицы в базе данных
        """
        ordering = ('user',)
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

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
        return reverse('profile_detail', kwargs={'slug': self.slug})