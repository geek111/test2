import time
from pathlib import Path
from typing import Dict

from .products import Product, ProductStore
from .notification import send_email
from .shops.base import ShopModule
from .shop_registry import ShopRegistry


class PriceTracker:
    """Main application class."""

    def __init__(self, store_path: str, interval: int = 3600,
                 email: str | None = None,
                 registry: ShopRegistry | None = None,
                 registry_path: str = 'shops.json') -> None:
        self.store = ProductStore(Path(store_path))
        self.registry = registry or ShopRegistry(Path(registry_path))
        self.shops: Dict[str, ShopModule] = self.registry.instantiate()
        self.interval = interval
        self.email = email

    def register_shop(self, name: str, shop: ShopModule,
                      class_path: str | None = None) -> None:
        self.shops[name] = shop
        if class_path:
            self.registry.add(name, class_path)

    def unregister_shop(self, name: str) -> None:
        """Remove a previously registered shop."""
        self.shops.pop(name, None)
        self.registry.remove(name)

    # Backwards-compatible alias
    add_shop = register_shop

    def add_product(self, name: str, url: str, shop: str) -> None:
        product = Product(name=name, url=url, shop=shop,
                          price_history=[], last_price=0.0)
        self.store.add(product)

    def check_prices(self) -> None:
        for product in self.store.products:
            shop = self.shops.get(product.shop)
            if not shop:
                print(f'Shop {product.shop} not registered')
                continue
            try:
                price = shop.get_price(product.url)
            except Exception as exc:
                print(f'Failed to fetch price for {product.name}: {exc}')
                continue

            previous_price = product.last_price
            self.store.update_price(product, price)
            print(f'{product.name}: {previous_price} -> {price}')

            if previous_price and price < previous_price:
                self.notify_price_drop(product, previous_price, price)

    def notify_price_drop(self, product: Product,
                          old: float, new: float) -> None:
        msg = (f'Price drop for {product.name}: {old} -> {new}\n'
               f'URL: {product.url}')
        if self.email:
            send_email(self.email, f'Price drop: {product.name}', msg)
        else:
            print(msg)

    def run(self) -> None:
        while True:
            self.check_prices()
            time.sleep(self.interval)
