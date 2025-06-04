import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class Product:
    name: str
    url: str
    shop: str
    price_history: List[float] = field(default_factory=list)
    last_price: float = 0.0


class ProductStore:
    def __init__(self, path: Path):
        self.path = path
        self.products: List[Product] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.products = []
            return
        data = json.loads(self.path.read_text())
        self.products = [Product(**item) for item in data.get('products', [])]

    def save(self) -> None:
        data = {'products': [vars(p) for p in self.products]}
        self.path.write_text(json.dumps(data, indent=2))

    def add(self, product: Product) -> None:
        self.products.append(product)
        self.save()

    def find_by_url(self, url: str) -> Product:
        for p in self.products:
            if p.url == url:
                return p
        raise ValueError(f'Product with url {url} not found')

    def update_price(self, product: Product, new_price: float) -> None:
        product.price_history.append(new_price)
        product.last_price = new_price
        self.save()

    def remove(self, url: str) -> None:
        """Remove a product matching ``url`` from the store."""
        for i, prod in enumerate(self.products):
            if prod.url == url:
                del self.products[i]
                self.save()
                return
        raise ValueError(f'Product with url {url} not found')
