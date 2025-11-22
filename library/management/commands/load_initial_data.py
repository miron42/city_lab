import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from library.models import Author, Book, Library


class Command(BaseCommand):
    help = "Загрузить авторов, книги и библиотеки из JSON"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default="library/data/initial_data.json",
            help="Путь до JSON файла",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f"Файл {path} не найден"))
            return

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        authors = data["authors"]
        books = data["books"]
        libraries = data["libraries"]

        self.stdout.write("Создаём авторов...")
        Author.objects.all().delete()
        Book.objects.all().delete()
        Library.objects.all().delete()

        Author.objects.bulk_create(
            [
                Author(
                    id=a["id"],
                    full_name=a["full_name"],
                    birth_date=a["birth_date"],
                )
                for a in authors
            ]
        )

        self.stdout.write("Создаём книги...")
        Book.objects.bulk_create(
            [
                Book(
                    id=b["id"],
                    title=b["title"],
                    year=b["year"],
                    author_id=b["author_id"],
                )
                for b in books
            ]
        )

        self.stdout.write("Создаём библиотеки...")
        Library.objects.bulk_create(
            [
                Library(
                    id=l["id"],
                    name=l["name"],
                    capacity=l["capacity"],
                )
                for l in libraries
            ]
        )

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))
