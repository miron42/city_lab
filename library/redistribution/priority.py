from typing import List
from .capacity import CapacityAwareRedistributionManager


class PriorityRedistributionManager(CapacityAwareRedistributionManager):
    """
    Менеджер перераспределения с приоритетами.
    Он меняет ТОЛЬКО стратегию выбора книги (pick_book),
    а сам алгоритм rebalance полностью наследует от CapacityAwareRedistributionManager.
    """

    PRIORITY_YEAR = 1950

    def pick_book(self, donor_id: int):
        """
        Переопределяем способ выбора книги у донора.

        Вместо "последней книги в списке" выбираем книгу с приоритетом:
        - сначала новые (year > PRIORITY_YEAR)
        - затем старые
        - внутри группы — по убыванию года (новее → раньше)
        """

        books = self.books_by_library[donor_id]

        sorted_books = sorted(
            books,
            key=lambda b: (b.year > self.PRIORITY_YEAR, b.year),
            reverse=True,
        )

        best_book = sorted_books[0]

        self.books_by_library[donor_id].remove(best_book)

        return best_book
