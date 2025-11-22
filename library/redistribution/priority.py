from typing import Iterable, List, Dict

from library.models import Library, LibraryBook
from .capacity import CapacityAwareRedistributionManager
from .move import Move


class PriorityRedistributionManager(CapacityAwareRedistributionManager):
    """
    Менеджер перераспределения с приоритетами выбора книги у донора.

    Пример стратегии по умолчанию:
        - сначала отдаём НОВЫЕ книги (год > 1950)
        - затем остальные

    При желании можно переопределить метод get_sorted_books().
    """

    PRIORITY_YEAR = 1950  # пример: приоритет отдавать новые книги

    def get_sorted_books(self, library_id: int):
        """
        Возвращает книги донора, отсортированные по приоритету.
        Можно перегрузить этот метод под любую стратегию.
        """

        books = self.books_by_library[library_id]

        # Пример стратегии:
        # 1) новые книги (year > PRIORITY_YEAR)
        # 2) остальные
        return sorted(
            books,
            key=lambda book: (book.year <= self.PRIORITY_YEAR, book.year),
            reverse=True,
        )
        # Ты можешь заменить эту стратегию на любую другую.

    def rebalance(self) -> List[Move]:
        """Тот же алгоритм, но с приоритетным выбором книги у донора."""
        moves: List[Move] = []

        while True:
            donors = sorted(
                [
                    lib
                    for lib in self.libraries.values()
                    if self.load[lib.id] > self.target_load[lib.id]
                ],
                key=lambda lib: self.load[lib.id] - self.target_load[lib.id],
                reverse=True,
            )

            receivers = sorted(
                [
                    lib
                    for lib in self.libraries.values()
                    if self.load[lib.id] < self.target_load[lib.id]
                ],
                key=lambda lib: self.target_load[lib.id] - self.load[lib.id],
                reverse=True,
            )

            if not donors or not receivers:
                break

            progress = False

            for donor in donors:
                donor_books = self.get_sorted_books(donor.id)

                for receiver in receivers:

                    if self.load[donor.id] <= self.target_load[donor.id]:
                        break

                    if self.load[receiver.id] >= self.target_load[receiver.id]:
                        continue

                    if not self.can_receive(receiver.id):
                        continue

                    if not donor_books:
                        break

                    # Берём книгу по приоритету
                    book = donor_books.pop(0)

                    # Обновляем состояние
                    self.books_by_library[donor.id].remove(book)
                    self.load[donor.id] -= 1
                    self.free[donor.id] += 1

                    self.books_by_library[receiver.id].append(book)
                    self.load[receiver.id] += 1
                    self.free[receiver.id] -= 1

                    moves.append(
                        Move(
                            book_id=book.id,
                            from_library_id=donor.id,
                            to_library_id=receiver.id,
                            quantity=1,
                        )
                    )

                    progress = True

            if not progress:
                break

        return moves
