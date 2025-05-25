# tests/test_reporting.py
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import date
import sys
sys.path.append('../')
from reporting import get_summary, get_monthly_revenue, get_income_between_dates
import mysql.connector

class TestReporting(unittest.TestCase):

    @patch('reporting.get_connection')
    def test_get_summary_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        # Atur return_value untuk setiap fetchone() sesuai urutan query
        mock_cursor.fetchone.side_effect = [
            (10,), # Total customers
            (25,), # Total orders
            (500000.0,) # Total income
        ]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        customers, orders, income = get_summary()
        self.assertEqual(customers, 10)
        self.assertEqual(orders, 25)
        self.assertEqual(income, 500000.0)
        
        # Cek apakah execute dipanggil 3 kali
        self.assertEqual(mock_cursor.execute.call_count, 3)
        mock_cursor.execute.assert_any_call("SELECT COUNT(*) FROM customers")
        mock_cursor.execute.assert_any_call("SELECT COUNT(*) FROM orders")
        mock_cursor.execute.assert_any_call("SELECT SUM(totalPrice) FROM orders")

    @patch('reporting.get_connection')
    def test_get_summary_no_income(self, mock_get_conn): # Kasus jika SUM(totalPrice) adalah NULL
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(5,), (10,), (None,)] # Total income NULL
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        _, _, income = get_summary()
        self.assertEqual(income, 0) # Harusnya jadi 0 jika NULL

    @patch('reporting.get_connection')
    def test_get_summary_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB Error")
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        customers, orders, income = get_summary()
        self.assertEqual(customers, 0)
        self.assertEqual(orders, 0)
        self.assertEqual(income, 0)

    @patch('reporting.get_connection')
    def test_get_monthly_revenue_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        # Data untuk DataFrame
        mock_cursor.fetchall.return_value = [
            ('2024-01', 150000.0),
            ('2024-02', 200000.0)
        ]
        expected_columns = ["Bulan", "Pendapatan"]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_revenue = get_monthly_revenue()
        self.assertIsInstance(df_revenue, pd.DataFrame)
        self.assertEqual(len(df_revenue), 2)
        self.assertListEqual(list(df_revenue.columns), expected_columns)
        mock_cursor.execute.assert_called_once() # Query panjang, cek pemanggilan saja

    @patch('reporting.get_connection')
    def test_get_monthly_revenue_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB Error")
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        df_revenue = get_monthly_revenue()
        self.assertTrue(df_revenue.empty)


    @patch('reporting.get_connection')
    def test_get_income_between_dates_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (125000.0,) # Total income pada rentang tanggal
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        start_d = date(2024, 1, 1)
        end_d = date(2024, 1, 31)
        income = get_income_between_dates(start_d, end_d)
        
        self.assertEqual(income, 125000.0)
        mock_cursor.execute.assert_called_with(
            # Query dari fungsi aslinya
            "\n            SELECT SUM(totalPrice) AS total_income\n            FROM orders\n            WHERE DATE(orderDate) BETWEEN %s AND %s \n            ",
            (start_d, end_d)
        )
    
    @patch('reporting.get_connection')
    def test_get_income_between_dates_no_income(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (None,) # Tidak ada income
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        income = get_income_between_dates(date(2024, 2, 1), date(2024, 2, 28))
        self.assertEqual(income, 0)

    @patch('reporting.get_connection')
    def test_get_income_between_dates_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB Error")
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        income = get_income_between_dates(date(2024, 3, 1), date(2024, 3, 31))
        self.assertEqual(income, 0)


if __name__ == '__main__':
    unittest.main()