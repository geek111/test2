import time
from pathlib import Path
from typing import Dict

from .products import Product, ProductStore
from .notification import send_email
from .shops.base import ShopModule


class PriceTracker:
    """Main application class."""

    def __init__(self, store_path: str, interval: int = 3600,
                 email: str | None = None) -> None:
        self.store = ProductStore(Path(store_path))
        self.shops: Dict[str, ShopModule] = {}
        self.interval = interval
        self.email = email
        self.paused = False

    def register_shop(self, name: str, shop: ShopModule) -> None:
        self.shops[name] = shop

    def add_product(self, name: str, url: str, shop: str) -> None:
        product = Product(name=name, url=url, shop=shop,
                          price_history=[], last_price=0.0)
        self.store.add(product)

    def remove_product(self, url: str) -> None:
        """Remove a tracked product by URL."""
        self.store.remove(url)

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

    def pause(self) -> None:
        """Pause automatic price checking."""
        self.paused = True

    def resume(self) -> None:
        """Resume automatic price checking."""
        self.paused = False

    def run(self) -> None:
        while True:
            if not self.paused:
                self.check_prices()
            time.sleep(self.interval)
