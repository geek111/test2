from .products import ProductStore

class Tracker:
    def __init__(self, store: ProductStore | None = None):
        self.store = store or ProductStore()

    def save(self) -> None:
        self.store.save()


def get_tracker() -> Tracker:
    return Tracker()
