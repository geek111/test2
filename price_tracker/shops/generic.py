import re
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
    return float(cleaned)

class GenericShop(ShopModule):
    """Shop module defined by a CSS selector."""

    def __init__(self, selector: str) -> None:
        self.selector = selector

    def get_price(self, url: str) -> float:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.select_one(self.selector)
        if element is None:
            raise ValueError(f'Price element not found using selector {self.selector}')
        price_text = element.text
        return parse_price(price_text)
