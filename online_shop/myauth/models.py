from django.contrib.auth.models import User
from django.db import models
from django.core.validators import FileExtensionValidator


def user_directory_path(instance, filename):
    return "user_{pk}/{filename}".format(pk=instance.user.id, filename=filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, verbose_name="Телефон")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Информация о себе")
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(
        verbose_name="Аватар",
        null=True,
        blank=True,
        upload_to=user_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=("png", "jpg", "jpeg"))],
    )

    # slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)

    class Meta:
        ordering = ("user",)
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
