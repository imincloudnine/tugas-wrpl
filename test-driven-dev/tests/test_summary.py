import pytest
from summary_logic import get_summary

def test_get_summary():
    total_customers, total_orders, total_income = get_summary()
    
    # Pastikan semua nilai bertipe benar
    assert isinstance(total_customers, int)
    assert isinstance(total_orders, int)
    assert isinstance(total_income, (int, float))

    # Asumsi dasarnya, tidak boleh negatif
    assert total_customers >= 0
    assert total_orders >= 0
    assert total_income >= 0
