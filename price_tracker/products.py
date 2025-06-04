from dataclasses import dataclass, asdict, field
from typing import List, Optional
import json
import os

@dataclass
class Product:
    name: str
    url: str
    price_history: List[float] = field(default_factory=list)
    last_price: Optional[float] = None

class ProductStore:
    def __init__(self, path: str = "products.json"):
        self.path = path
        self.products: List[Product] = []
        self.load()

    def load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.products = [Product(**p) for p in data]

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump([asdict(p) for p in self.products], fh, indent=2)

    def find_by_url(self, url: str) -> Optional[Product]:
        for p in self.products:
            if p.url == url:
                return p
        return None

    def update_price(self, product: Product, price: float) -> None:
        product.price_history.append(price)
        product.last_price = price
        self.save()

    def set_price(self, product: Product, price: float) -> None:
        """Set product price without fetching.

        Updates price_history and last_price similarly to update_price.
        """
        self.update_price(product, price)
