from price_tracker.tracker import PriceTracker


def main() -> None:
    tracker = PriceTracker('products.json', interval=3600, shops_path='shops.json')

    # Example of adding a product
    # tracker.add_product('Example Product', 'http://example.com/product', 'shopa')

    tracker.run()


if __name__ == '__main__':
    main()
