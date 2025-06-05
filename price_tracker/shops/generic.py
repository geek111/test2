import requests
from bs4 import BeautifulSoup

from .base import ShopModule

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
        price_text = element.text.strip()
        return float(price_text.replace('$', '').replace(',', ''))
