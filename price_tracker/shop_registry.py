import json
from importlib import import_module
from pathlib import Path
from typing import Dict

from .shops.base import ShopModule


class ShopRegistry:
    """Persisted registry of shop plugins."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.shops: Dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            self.shops = json.loads(self.path.read_text())
        else:
            self.shops = {}

    def save(self) -> None:
        self.path.write_text(json.dumps(self.shops, indent=2))

    def add(self, name: str, class_path: str) -> None:
        self.shops[name] = class_path
        self.save()

    def remove(self, name: str) -> None:
        self.shops.pop(name, None)
        self.save()

    def instantiate(self) -> Dict[str, ShopModule]:
        """Instantiate all registered shop modules."""
        result: Dict[str, ShopModule] = {}
        for name, class_path in self.shops.items():
            module_name, class_name = class_path.split(":")
            module = import_module(module_name)
            cls = getattr(module, class_name)
            result[name] = cls()
        return result
