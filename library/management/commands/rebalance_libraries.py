from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import transaction

from library.models import Library, LibraryBook
from library.redistribution.capacity import CapacityAwareRedistributionManager
from library.redistribution.priority import PriorityRedistributionManager


class Command(BaseCommand):
    help = "Полное перераспределение книг между библиотеками (вариант A): пересборка таблицы LibraryBook."

    def _print_state(self, libraries, load, title="Состояние"):
        total = sum(load.values())
        self.stdout.write(f"\n=== {title} ===")
        self.stdout.write(f"Всего книг в системе: {total}\n")

        for lib in libraries:
            count = load.get(lib.id, 0)
            capacity = lib.capacity
            percent = (count / capacity * 100) if capacity > 0 else 0

            self.stdout.write(
                f"{lib.name:30} {count:3d}/{capacity:3d}  " f"({percent:5.1f}%)"
            )

    def handle(self, *args, **options):
        self.stdout.write("Загрузка библиотек и инвентаря...")

        libraries = list(Library.objects.all())
        inventory = list(LibraryBook.objects.select_related("book", "library"))

        # Загружаем текущую загрузку
        load_before = defaultdict(int)
        for lb in inventory:
            load_before[lb.library_id] += 1

        # Вывод состояния ДО
        self._print_state(libraries, load_before, "ДО перераспределения")

        # Менеджер перераспределения
        mgr = PriorityRedistributionManager(libraries, inventory)

        # Выполняем перераспределение (создаёт локальное новое состояние)
        mgr.rebalance()

        # Теперь mgr.books_by_library содержит правильное распределение
        self.stdout.write("\nПерестраиваем таблицу LibraryBook...")

        # Полная пересборка таблицы
        with transaction.atomic():
            LibraryBook.objects.all().delete()

            new_records = []
            for lib_id, books in mgr.books_by_library.items():
                for book in books:
                    new_records.append(LibraryBook(library_id=lib_id, book_id=book.id))

            LibraryBook.objects.bulk_create(new_records)

        # Загружаем новое распределение
        new_inventory = list(LibraryBook.objects.all())
        load_after = defaultdict(int)
        for lb in new_inventory:
            load_after[lb.library_id] += 1

        # Вывод состояния ПОСЛЕ
        self._print_state(libraries, load_after, "ПОСЛЕ перераспределения")

        self.stdout.write(
            self.style.SUCCESS("\nПерераспределение завершено (вариант A).")
        )
