# tests/test_product_management.py
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
sys.path.append('../')
from product_management import (
    get_all_products, update_stock, get_bunga_list, 
    get_low_stock_products, update_bunga_price, get_top_selling_products
)
import mysql.connector

class TestProductManagement(unittest.TestCase):

    @patch('product_management.get_connection')
    def test_get_all_products_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        # dictionary=True, jadi fetchall mengembalikan list of dicts
        mock_cursor.fetchall.return_value = [
            {'bungaID': 1, 'bungaName': 'Rose', 'hargaPerTangkai': 10000, 'stock': 50},
            {'bungaID': 2, 'bungaName': 'Lily', 'hargaPerTangkai': 12000, 'stock': 30}
        ]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        products = get_all_products()
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]['bungaName'], 'Rose')
        mock_cursor.execute.assert_called_with("SELECT bungaID, bungaName, hargaPerTangkai, stock FROM products")

    @patch('product_management.get_connection')
    def test_get_all_products_empty(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        products = get_all_products()
        self.assertEqual(len(products), 0)

    @patch('product_management.get_connection')
    def test_get_all_products_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB Error")
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        products = get_all_products()
        self.assertEqual(len(products), 0) # Harusnya return list kosong

    @patch('product_management.get_connection')
    def test_update_stock_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = update_stock(1, 10) # bungaID=1, tambahStock=10
        self.assertTrue(result)
        mock_cursor.callproc.assert_called_with("UpdateProductStock", (1, 10))
        mock_conn_instance.commit.assert_called_once()

    @patch('product_management.get_connection')
    def test_update_stock_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.callproc.side_effect = mysql.connector.Error("Error calling UpdateProductStock")
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = update_stock(1, 10)
        self.assertFalse(result)
        self.assertFalse(mock_conn_instance.commit.called) # Commit tidak boleh dipanggil jika callproc error

    @patch('product_management.get_connection')
    def test_get_bunga_list_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'bungaID': 1, 'bungaName': 'Rose'}, {'bungaID': 2, 'bungaName': 'Lily'}
        ]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        bunga_list = get_bunga_list()
        self.assertEqual(len(bunga_list), 2)
        self.assertEqual(bunga_list[0]['bungaName'], 'Rose')
        mock_cursor.execute.assert_called_with("SELECT bungaID, bungaName FROM products")

    @patch('product_management.get_connection')
    def test_get_low_stock_products_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('Tulip', 3), ('Orchid', 5)] # Data untuk DataFrame
        expected_columns = ["Nama Bunga", "Stok"]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_low_stock = get_low_stock_products(threshold=5)
        self.assertIsInstance(df_low_stock, pd.DataFrame)
        self.assertEqual(len(df_low_stock), 2)
        self.assertListEqual(list(df_low_stock.columns), expected_columns)
        mock_cursor.execute.assert_called_with(
            "SELECT bungaName, stock FROM products WHERE stock <= %s ORDER BY stock ASC", (5,)
        )
    
    @patch('product_management.get_connection')
    def test_get_low_stock_products_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB Error")
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_low_stock = get_low_stock_products(threshold=5)
        self.assertTrue(df_low_stock.empty)


    @patch('product_management.get_connection')
    def test_update_bunga_price_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = update_bunga_price(1, 15000.0) # bungaID=1, new_price=15000.0
        self.assertTrue(result)
        mock_cursor.execute.assert_called_with(
            "UPDATE products SET hargaPerTangkai = %s WHERE bungaID = %s", (15000.0, 1)
        )
        mock_conn_instance.commit.assert_called_once()

    @patch('product_management.get_connection')
    def test_get_top_selling_products_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('Rose', 100), ('Lily', 75)]
        expected_columns = ["Nama Bunga", "Total Terjual"]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_top = get_top_selling_products()
        self.assertIsInstance(df_top, pd.DataFrame)
        self.assertEqual(len(df_top), 2)
        self.assertListEqual(list(df_top.columns), expected_columns)
        # Query panjang, jadi kita hanya cek apakah execute dipanggil
        mock_cursor.execute.assert_called_once() 


if __name__ == '__main__':
    unittest.main()