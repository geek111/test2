import argparse
from pathlib import Path

from price_tracker.tracker import PriceTracker
from price_tracker.shop_registry import ShopRegistry


def get_tracker() -> PriceTracker:
    registry = ShopRegistry(Path('shops.json'))
    tracker = PriceTracker('products.json', registry=registry)
    return tracker


def cmd_add_shop(args: argparse.Namespace) -> None:
    registry = ShopRegistry(Path('shops.json'))
    registry.add(args.name, args.class_path)
    print(f"Registered shop '{args.name}' -> {args.class_path}")


def cmd_remove_shop(args: argparse.Namespace) -> None:
    registry = ShopRegistry(Path('shops.json'))
    registry.remove(args.name)
    print(f"Removed shop '{args.name}'")


def cmd_add_product(args: argparse.Namespace) -> None:
    tracker = get_tracker()
    tracker.add_product(args.name, args.url, args.shop)
    print(f"Added product '{args.name}' for shop '{args.shop}'")


def cmd_run(args: argparse.Namespace) -> None:
    tracker = get_tracker()
    tracker.run()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Price tracker")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run the tracker loop")
    run_p.set_defaults(func=cmd_run)

    add_shop_p = sub.add_parser("add-shop", help="Register a new shop")
    add_shop_p.add_argument("name")
    add_shop_p.add_argument("class_path", help="Python path to shop class")
    add_shop_p.set_defaults(func=cmd_add_shop)

    remove_shop_p = sub.add_parser("remove-shop", help="Unregister a shop")
    remove_shop_p.add_argument("name")
    remove_shop_p.set_defaults(func=cmd_remove_shop)

    add_product_p = sub.add_parser("add-product", help="Add a product to track")
    add_product_p.add_argument("name")
    add_product_p.add_argument("url")
    add_product_p.add_argument("shop")
    add_product_p.set_defaults(func=cmd_add_product)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
