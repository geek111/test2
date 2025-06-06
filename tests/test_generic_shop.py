import os
import sys
import requests
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from price_tracker.shops.generic import GenericShop


class MockResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def make_get(html):
    def _get(url):
        return MockResponse(html)
    return _get


def test_price_from_text(monkeypatch):
    html = "<span class='price'>29,99 zł</span>"
    monkeypatch.setattr(requests, 'get', make_get(html))
    shop = GenericShop('span.price')
    assert shop.get_price('http://example.com') == 29.99


def test_price_from_data_attribute(monkeypatch):
    html = "<div class='p' data-product-gtm='{\"current_price\": \"123,45\"}'></div>"
    monkeypatch.setattr(requests, 'get', make_get(html))
    shop = GenericShop('div.p')
    assert shop.get_price('http://example.com') == 123.45


def test_price_from_jsonld(monkeypatch):
    html = (
        "<script type='application/ld+json'>{"
        "\"offers\": {\"price\": 49.99, \"priceCurrency\": \"PLN\"}}"
        "</script>"
    )
    monkeypatch.setattr(requests, 'get', make_get(html))
    # Selector not found, should still parse from JSON-LD
    shop = GenericShop('span.price')
    assert shop.get_price('http://example.com') == 49.99
