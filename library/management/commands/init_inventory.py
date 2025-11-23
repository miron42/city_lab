import random
from collections import defaultdict
from django.core.management.base import BaseCommand

from library.models import Book, Library, LibraryBook


class Command(BaseCommand):
    help = "Разместить книги по библиотекам и вывести первичное распределение"

    def _print_libraries_state(self, libraries, counts):
        self.stdout.write("\n=== Первичное распределение книг ===")
        total_books = sum(counts.values())
        self.stdout.write(f"Всего книг в системе: {total_books}\n")

        for lib in libraries:
            load = counts[lib.id]
            capacity = lib.capacity
            percent = (load / capacity * 100) if capacity > 0 else 0
            self.stdout.write(
                f"{lib.name:30} {load:3d}/{capacity:3d}  ({percent:5.1f}%)"
            )

    def handle(self, *args, **options):
        # Загружаем библиотеки и книги из БД
        libraries = list(Library.objects.all())
        books = list(Book.objects.all())

        # очищаем старые размещения
        LibraryBook.objects.all().delete()

        # создаём словарь для подсчёта загрузки
        # пока что 0 книг в каждой библиотеке
        load = {lib.id: 0 for lib in libraries}

        # iter - перебор с ручным управление
        lib_iter = iter(libraries)
        current = next(lib_iter)

        for book in books:
            # если текущая библиотека переполнена — берём следующую
            if load[current.id] >= current.capacity:
                current = next(lib_iter)

            # размещаем книгу
            LibraryBook.objects.create(library=current, book=book)
            load[current.id] += 1

        # вывод первичного распределения
        self._print_libraries_state(libraries, load)

        self.stdout.write(self.style.SUCCESS("\nПервичное распределение завершено"))
