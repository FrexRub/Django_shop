from uuid import uuid4
from pytils.translit import slugify
from django.core.exceptions import ValidationError

MAX_SIZE_FILE = 2


def unique_slugify(instance, slug):
    """
    Генератор уникальных SLUG для моделей, в случае существования такого SLUG.
    """
    model = instance.__class__
    unique_slug = slugify(slug)
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{unique_slug}-{uuid4().hex[:8]}'
    return unique_slug


def validate_file_size(value):
    filesize = value.size

    if filesize > MAX_SIZE_FILE * 1024 * 1024:
        raise ValidationError(f"You cannot upload file more than {MAX_SIZE_FILE}Mb")
