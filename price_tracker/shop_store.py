import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

@dataclass
class ShopDef:
    name: str
    selector: str

class ShopStore:
    """Persist shop definitions to a JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.shops: Dict[str, ShopDef] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.shops = {}
            return
        data = json.loads(self.path.read_text())
        self.shops = {
            name: ShopDef(name=name, selector=sel)
            for name, sel in data.get('shops', {}).items()
        }

    def save(self) -> None:
        data = {'shops': {name: shop.selector for name, shop in self.shops.items()}}
        self.path.write_text(json.dumps(data, indent=2))

    def add(self, shop: ShopDef) -> None:
        self.shops[shop.name] = shop
        self.save()

    def update(self, shop: ShopDef) -> None:
        self.shops[shop.name] = shop
        self.save()

    def remove(self, name: str) -> None:
        if name not in self.shops:
            raise ValueError(f'Shop {name} not found')
        del self.shops[name]
        self.save()

    def rename(self, old_name: str, new_name: str) -> None:
        """Rename a shop definition."""
        if old_name not in self.shops:
            raise ValueError(f'Shop {old_name} not found')
        if new_name in self.shops:
            raise ValueError(f'Shop {new_name} already exists')
        shop = self.shops.pop(old_name)
        shop.name = new_name
        self.shops[new_name] = shop
        self.save()
