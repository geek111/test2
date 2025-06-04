import argparse
from price_tracker.tracker import get_tracker


def main() -> None:
    parser = argparse.ArgumentParser(description="Price Tracker")
    sub = parser.add_subparsers(dest="cmd")

    set_price_p = sub.add_parser("set-price", help="Set the price of a product")
    set_price_p.add_argument("url", help="Product URL")
    set_price_p.add_argument("price", type=float, help="New price")

    args = parser.parse_args()

    if args.cmd == "set-price":
        tracker = get_tracker()
        product = tracker.store.find_by_url(args.url)
        if not product:
            raise SystemExit("Product not found")
        tracker.store.set_price(product, args.price)
        print(f"Set price for {product.url} to {args.price}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
