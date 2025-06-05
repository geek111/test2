import requests
from bs4 import BeautifulSoup

from .base import ShopModule
from .generic import parse_price

class ShopA(ShopModule):
    """Example shop implementation."""

    def get_price(self, url: str) -> float:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Example: price contained in span with class 'price'
        price_text = soup.select_one('span.price').text
        return parse_price(price_text)
