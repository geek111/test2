import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from price_tracker.shops.generic import parse_price

@pytest.mark.parametrize('text,expected', [
    ('29.99,', 29.99),
    ('29,99 zł', 29.99),
    ('1 234,56 zł', 1234.56),
    ('1.234,56 zł', 1234.56),
    ('1 234.56$', 1234.56),
    ('K-Beauty 2.0', 2.0),
])
def test_parse_price(text, expected):
    assert parse_price(text) == expected
