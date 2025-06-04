from price_tracker.tracker import PriceTracker
from price_tracker.shops.shop_a import ShopA
from price_tracker.shops.shop_b import ShopB


def main() -> None:
    tracker = PriceTracker('products.json', interval=3600)
    tracker.register_shop('shopa', ShopA())
    tracker.register_shop('shopb', ShopB())

    # Example of adding a product
    # tracker.add_product('Example Product', 'http://example.com/product', 'shopa')

    tracker.run()


if __name__ == '__main__':
    main()
