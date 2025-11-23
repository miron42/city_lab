from .base import RedistributionManager


class CapacityAwareRedistributionManager(RedistributionManager):

    def __init__(self, libraries, inventory):
        super().__init__(libraries, inventory)
        self.free = {
            lib.id: lib.capacity - self.load[lib.id] for lib in self.libraries.values()
        }

    def can_receive(self, library_id: int) -> bool:
        return self.free[library_id] > 0

    def on_move_planned(self, donor_id: int, receiver_id: int):
        self.free[donor_id] += 1
        self.free[receiver_id] -= 1
