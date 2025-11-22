from collections import defaultdict
from typing import Iterable, List, Dict

from library.models import Library, LibraryBook
from .move import Move


class RedistributionManager:
    """
    Базовый перераспределитель:
    - высчитывает target_load пропорционально capacity
    - переносит книги до стабилизации
    - НЕ учитывает capacity (это делает CapacityAwareRedistributionManager)
    """

    def __init__(self, libraries: Iterable[Library], inventory: Iterable[LibraryBook]):
        # Сохраняем библиотеки в словарь по ID
        self.libraries: Dict[int, Library] = {lib.id: lib for lib in libraries}

        # Инвентарь
        self.inventory: List[LibraryBook] = list(inventory)

        # Счётчики книг
        self.load = defaultdict(int)  # сколько книг в библиотеке
        self.books_by_library = defaultdict(list)  # список книг в библиотеке

        # Заполняем load + books_by_library
        for lb in self.inventory:
            self.load[lb.library_id] += 1
            self.books_by_library[lb.library_id].append(lb.book)

        # Общие показатели
        self.total_books = sum(self.load.values())
        self.total_capacity = sum(lib.capacity for lib in libraries)

        # Целевое распределение по формуле:
        #   target_load = round( total_books * capacity / total_capacity )
        self.target_load = {
            lib.id: round(self.total_books * lib.capacity / self.total_capacity)
            for lib in self.libraries.values()
        }

    def rebalance(self) -> List[Move]:
        """
        Полное перераспределение до стабилизации.
        НЕ проверяет свободное место — только чистая пропорциональность.
        """
        moves: List[Move] = []

        # Выполняем, пока можно что-то перенести
        while True:

            # Доноры: у кого load > target
            donors = sorted(
                [
                    lib
                    for lib in self.libraries.values()
                    if self.load[lib.id] > self.target_load[lib.id]
                ],
                key=lambda lib: self.load[lib.id] - self.target_load[lib.id],
                reverse=True,
            )

            # Реципиенты: у кого load < target
            receivers = sorted(
                [
                    lib
                    for lib in self.libraries.values()
                    if self.load[lib.id] < self.target_load[lib.id]
                ],
                key=lambda lib: self.target_load[lib.id] - self.load[lib.id],
                reverse=True,
            )

            # Если никто не нуждается в перераспределении → закончили
            if not donors or not receivers:
                break

            progress = False  # флаг для выхода, если ничего не поменялось

            # Основной цикл перераспределения
            for donor in donors:
                for receiver in receivers:

                    # донор уже дал достаточно
                    if self.load[donor.id] <= self.target_load[donor.id]:
                        break

                    # реципиент уже получил достаточно
                    if self.load[receiver.id] >= self.target_load[receiver.id]:
                        continue

                    # у донора может не остаться книг
                    if not self.books_by_library[donor.id]:
                        continue

                    # Берём книгу
                    book = self.books_by_library[donor.id].pop()

                    # Обновление нагрузки
                    self.load[donor.id] -= 1
                    self.load[receiver.id] += 1
                    self.books_by_library[receiver.id].append(book)

                    # Регистрируем перемещение
                    moves.append(
                        Move(
                            book_id=book.id,
                            from_library_id=donor.id,
                            to_library_id=receiver.id,
                            quantity=1,
                        )
                    )

                    progress = True

            # Если на этом проходе ничего не перенесли → баланс достигнут
            if not progress:
                break

        return moves
