from abc import ABC, abstractmethod

class ShopModule(ABC):
    """Base class for shop modules."""

    @abstractmethod
    def get_price(self, url: str) -> float:
        """Return current price for the product at ``url``."""
        raise NotImplementedError
