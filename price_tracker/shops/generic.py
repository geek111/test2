import re
import json
import requests
from bs4 import BeautifulSoup

from .base import ShopModule


def parse_price(text: str) -> float:
    """Clean a price string and convert it to ``float``.

    The function removes currency identifiers (zł, PLN, €, $, etc.),
    strips whitespace, replaces comma with a dot and removes thousands
    separators (space or non‑breaking space).
    """
    cleaned = text.strip()
    cleaned = re.sub(r"(?i)(zł|pln|eur|euro|usd|\$|€|gbp|£)", "", cleaned)
    cleaned = cleaned.replace("\xa0", "").replace(" ", "")
    cleaned = cleaned.replace(",", ".")
    cleaned = re.sub(r"[^0-9.\-]", "", cleaned)
    cleaned = cleaned.strip(".")
    if cleaned.count(".") > 1:
        last = cleaned.rfind(".")
        cleaned = cleaned[:last].replace(".", "") + cleaned[last:]
    if not cleaned or cleaned == ".":
        raise ValueError(f"Could not parse price: {text}")
    return float(cleaned)


def _find_price_in_json(data):
    """Recursively search for price fields in a JSON object."""
    if isinstance(data, dict):
        for key in (
            "price",
            "current_price",
            "lowPrice",
            "highPrice",
        ):
            if key in data and isinstance(data[key], (str, int, float)):
                return data[key]
        for value in data.values():
            found = _find_price_in_json(value)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = _find_price_in_json(item)
            if found is not None:
                return found
    return None

class GenericShop(ShopModule):
    """Shop module defined by a CSS selector."""

    def __init__(self, selector: str) -> None:
        self.selector = selector

    def get_price(self, url: str) -> float:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.select_one(self.selector)

        price_text = (element.text or '').strip() if element else ''
        if price_text:
            try:
                price = parse_price(price_text)
                if price:
                    return price
            except Exception:
                pass

        # Fallback: some shops store the price in data attributes like
        # "data-product-gtm" as JSON with fields such as "current_price".
        if element:
            for attr in ('data-product-gtm', 'data-product', 'data-gtm'):
                attr_val = element.get(attr)
                if not attr_val:
                    continue
                match = re.search(r'"current_price"\s*:\s*"?([0-9.,]+)"?', attr_val)
                if not match:
                    match = re.search(r'"price"\s*:\s*"?([0-9.,]+)"?', attr_val)
                if match:
                    return parse_price(match.group(1))

        # Fallback to JSON-LD scripts
        for script in soup.find_all('script', type='application/ld+json'):
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
            except Exception:
                continue
            val = _find_price_in_json(data)
            if val is not None:
                return parse_price(str(val))

        if element is None:
            raise ValueError(f'Price element not found using selector {self.selector}')
        raise ValueError('Price not found in element or JSON-LD')
