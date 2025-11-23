from collections import defaultdict
from typing import List
from library.models import Library, LibraryBook
from .move import Move


class RedistributionManager:
    """
    Базовый распределитель.
    Выполняет перераспределение, опираясь только на target_load.
    Может быть расширен за счёт переопределения нескольких методов.
    """

    def __init__(self, libraries, inventory):
        self.libraries = {lib.id: lib for lib in libraries}
        self.inventory = list(inventory)

        self.load = defaultdict(int)
        self.books_by_library = defaultdict(list)

        for lb in self.inventory:
            self.load[lb.library_id] += 1
            self.books_by_library[lb.library_id].append(lb.book)

        self.total_books = sum(self.load.values())
        self.total_capacity = sum(lib.capacity for lib in libraries)

        self.target_load = {
            lib.id: round(self.total_books * lib.capacity / self.total_capacity)
            for lib in self.libraries.values()
        }

    # Методы для наследников

    def can_receive(self, library_id: int) -> bool:
        """Можно ли принять книгу? Базовая версия разрешает всё."""
        return True

    def on_move_planned(self, donor_id: int, receiver_id: int):
        """Хук, вызываемый при планировании переноса. Базовая версия пустая."""
        pass

    def pick_book(self, donor_id: int):
        """Какую книгу донор отдаёт? Базовая версия — последнюю."""
        return self.books_by_library[donor_id].pop()

    # Распределение
    def rebalance(self) -> List[Move]:
        moves = []

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
                for receiver in receivers:

                    donor_id = donor.id
                    receiver_id = receiver.id

                    if self.load[donor_id] <= self.target_load[donor_id]:
                        break

                    if self.load[receiver_id] >= self.target_load[receiver_id]:
                        continue

                    if not self.books_by_library[donor_id]:
                        continue

                    if not self.can_receive(receiver_id):
                        continue

                    book = self.pick_book(donor_id)

                    self.load[donor_id] -= 1
                    self.load[receiver_id] += 1
                    self.books_by_library[receiver_id].append(book)

                    self.on_move_planned(donor_id, receiver_id)

                    moves.append(
                        Move(
                            book_id=book.id,
                            from_library_id=donor_id,
                            to_library_id=receiver_id,
                            quantity=1,
                        )
                    )

                    progress = True

            if not progress:
                break

        return moves
