import random
from collections import defaultdict
from django.core.management.base import BaseCommand

from library.models import Book, Library, LibraryBook


class Command(BaseCommand):
    help = "Разместить книги по библиотекам и вывести первичное распределение"

    def _print_libraries_state(self, libraries, counts):
        self.stdout.write("\n=== Первичное распределение книг ===")
        total = sum(counts.values())
        self.stdout.write(f"Всего книг в системе: {total}\n")

        for lib in libraries:
            load = counts[lib.id]
            bar = f"[{'#' * load}{'.' * (lib.capacity - load)}]"
            self.stdout.write(f"{lib.name:30} {load:3d}/{lib.capacity:3d} {bar}")

    def handle(self, *args, **options):
        libraries = list(Library.objects.all())
        books = list(Book.objects.all())

        # очищаем старые размещения
        LibraryBook.objects.all().delete()

        # создаём словарь для подсчёта загрузки
        load = {lib.id: 0 for lib in libraries}

        lib_iter = iter(libraries)
        current = next(lib_iter)

        for book in books:
            # если текущая библиотека переполнена — берём следующую
            if load[current.id] >= current.capacity:
                try:
                    current = next(lib_iter)
                except StopIteration:
                    raise ValueError(
                        "Суммарная capacity библиотек меньше, чем количество книг!"
                    )

            # размещаем книгу
            LibraryBook.objects.create(library=current, book=book)
            load[current.id] += 1

        # вывод первичного распределения
        self._print_libraries_state(libraries, load)

        self.stdout.write(self.style.SUCCESS("\nПервичное распределение завершено"))
