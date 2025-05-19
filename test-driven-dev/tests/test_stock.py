import pytest
from BouquetShop import update_stock, get_stock_level

def test_update_stock():
    bunga_id = 1  # ID bunga contoh
    initial_stock = get_stock_level(bunga_id)
    added_stock = 5
    update_stock(bunga_id, added_stock)
    new_stock = get_stock_level(bunga_id)
    assert new_stock == initial_stock + added_stock
