from django.contrib.auth.models import User
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.validators import RegexValidator

from services.utils import unique_slugify

MAX_SIZE_FILE = 2
phone_number_validator = RegexValidator(
    r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"
)


def validate_file_size(value):
    filesize = value.size

    if filesize > MAX_SIZE_FILE * 1024 * 1024:
        raise ValidationError(f"You cannot upload file more than {MAX_SIZE_FILE}Mb")


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
        Сортировка, название таблицы в базе данных
        """

        ordering = ("user",)
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

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
