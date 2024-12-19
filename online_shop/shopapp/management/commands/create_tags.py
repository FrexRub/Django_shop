from pathlib import Path

from django.core.management import BaseCommand

from shopapp.models import Tag

BASE_DIR = Path(__file__).parent.parent.parent.parent


class Command(BaseCommand):
    """
    Creates tags
    """

    def handle(self, *args, **options):
        self.stdout.write("Start create tags")
        file_tags: str = BASE_DIR / "data_files" / "tags.txt"
        tags_names: list[str] = []
        with open(file_tags, encoding="utf-8") as file:
            tags = file.readlines()
            for i_tag in tags:
                tags_names.append(i_tag.strip())

        for tag_name in tags_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(f"Created tag {tag.name}")

        self.stdout.write(self.style.SUCCESS("Tags created"))
