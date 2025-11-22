from dataclasses import dataclass


@dataclass
class Move:
    book_id: int
    from_library_id: int
    to_library_id: int
    quantity: int = 1
