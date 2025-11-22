from typing import Iterable, List, Dict
from collections import defaultdict

from library.models import Library, LibraryBook
from .base import RedistributionManager
from .move import Move


class CapacityAwareRedistributionManager(RedistributionManager):
    """
    Менеджер перераспределения, который:
    - распределяет книги пропорционально capacity библиотек;
    - учитывает, что библиотека не может принять больше, чем capacity;
    - выполняет перераспределение до стабилизации (пока можно перемещать).
    """

    def __init__(self, libraries: Iterable[Library], inventory: Iterable[LibraryBook]):
        super().__init__(libraries, inventory)

        # Сколько свободного места осталось
        self.free = {
            lib.id: lib.capacity - self.load[lib.id] for lib in self.libraries.values()
        }

    def can_receive(self, library_id: int) -> bool:
        """Проверка, может ли библиотека получить ещё книгу."""
        return self.free[library_id] >= 1

    def rebalance(self) -> List[Move]:
        moves: List[Move] = []

        # Запускаем цикл до стабилизации
        while True:
            # --- Пересчёт доноров ---
            donors = sorted(
                [
                    lib
                    for lib in self.libraries.values()
                    if self.load[lib.id] > self.target_load[lib.id]
                ],
                key=lambda lib: self.load[lib.id] - self.target_load[lib.id],
                reverse=True,
            )

            # --- Пересчёт реципиентов ---
            receivers = sorted(
                [
                    lib
                    for lib in self.libraries.values()
                    if self.load[lib.id] < self.target_load[lib.id]
                ],
                key=lambda lib: self.target_load[lib.id] - self.load[lib.id],
                reverse=True,
            )

            # Никто никому не должен — баланс
            if not donors or not receivers:
                break

            progress = False  # были ли перемещения в этой итерации

            # --- Основной алгоритм ---
            for donor in donors:
                for receiver in receivers:

                    # донор отдал достаточно
                    if self.load[donor.id] <= self.target_load[donor.id]:
                        break

                    # реципиент получил достаточно
                    if self.load[receiver.id] >= self.target_load[receiver.id]:
                        continue

                    # capacity-aware ограничение
                    if not self.can_receive(receiver.id):
                        continue

                    # у донора закончились книги
                    if not self.books_by_library[donor.id]:
                        continue

                    # Берём книгу у донора
                    book = self.books_by_library[donor.id].pop()

                    # Обновляем локальные данные
                    self.load[donor.id] -= 1
                    self.free[donor.id] += 1

                    self.load[receiver.id] += 1
                    self.free[receiver.id] -= 1
                    self.books_by_library[receiver.id].append(book)

                    # Регистрируем перенос
                    moves.append(
                        Move(
                            book_id=book.id,
                            from_library_id=donor.id,
                            to_library_id=receiver.id,
                            quantity=1,
                        )
                    )

                    progress = True

            # Если ничего не перенесли — достигнута стабилизация
            if not progress:
                break

        return moves
