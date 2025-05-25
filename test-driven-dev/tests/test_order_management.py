# tests/test_order_management.py
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import date # Untuk tes get_orders dengan tanggal
import sys
sys.path.append('../')
from order_management import (
    create_new_order, get_orders, update_order_status, 
    get_order_details_table, get_customer_orders_history, 
    get_last_five_orders, get_full_order_details_for_customer, cancel_order
)
import mysql.connector

class TestOrderManagement(unittest.TestCase):

    @patch('order_management.get_connection')
    def test_create_new_order_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = create_new_order(1, "Cash", 1, 5, "Pink")
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Pesanan berhasil dibuat!")
        mock_cursor.callproc.assert_called_with("CreateNewOrder", (1, "Cash", 1, 5, "Pink"))
        mock_conn_instance.commit.assert_called_once()

    @patch('order_management.get_connection')
    def test_create_new_order_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.callproc.side_effect = mysql.connector.Error("Error in CreateNewOrder")
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = create_new_order(1, "OVO", 2, 3, "Blue")
        self.assertFalse(result["success"])
        self.assertIn("Error in CreateNewOrder", result["message"])
        self.assertFalse(mock_conn_instance.commit.called)

    @patch('order_management.get_connection')
    def test_get_orders_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        # Data untuk DataFrame
        mock_cursor.fetchall.return_value = [
            (101, 1, date(2024, 1, 15), 'Completed', 50000.0, 'Cash'),
            (102, 2, date(2024, 1, 16), 'Pending', 75000.0, 'OVO')
        ]
        expected_columns = ["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_orders = get_orders(search_query="10", status="Completed", order_date=date(2024, 1, 15), payment_method="Cash")
        self.assertIsInstance(df_orders, pd.DataFrame)
        # Jika data di atas tidak cocok dengan filter, df_orders bisa kosong.
        # Untuk tes ini, kita asumsikan query akan dieksekusi.
        # Kita lebih fokus pada pemanggilan execute dan pembuatan DataFrame.
        mock_cursor.execute.assert_called_once() 
        # Jika fetchall mengembalikan data di atas, maka len(df_orders) akan 2.
        self.assertEqual(len(df_orders), 2) 
        self.assertListEqual(list(df_orders.columns), expected_columns)


    @patch('order_management.get_connection')
    def test_get_orders_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB Error")
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        df_orders = get_orders()
        self.assertTrue(df_orders.empty)


    @patch('order_management.get_connection')
    def test_update_order_status_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = update_order_status(101, "Shipped")
        self.assertTrue(result)
        mock_cursor.callproc.assert_called_with("UpdateOrderStatus", (101, "Shipped"))
        mock_conn_instance.commit.assert_called_once()

    @patch('order_management.get_connection')
    def test_get_order_details_table_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, 101, 1, 5, 10000.0, "Pink"),
            (2, 101, 2, 2, 12000.0, "None")
        ]
        expected_columns = ["Order Details ID", "Order ID", "Bunga ID", "Kuantitas Tangkai", "Harga Unit", "Custom"]

        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_details = get_order_details_table(search_orderID="101")
        self.assertIsInstance(df_details, pd.DataFrame)
        self.assertEqual(len(df_details), 2)
        self.assertListEqual(list(df_details.columns), expected_columns)
        mock_cursor.execute.assert_called_once()

    @patch('order_management.get_connection')
    def test_get_customer_orders_history_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
             (101, 1, date(2024, 1, 15), 'Completed', 50000.0, 'Cash')
        ]
        expected_columns = ["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_history = get_customer_orders_history(1)
        self.assertIsInstance(df_history, pd.DataFrame)
        self.assertEqual(len(df_history), 1)
        self.assertListEqual(list(df_history.columns), expected_columns)
        mock_cursor.execute.assert_called_with(
            "SELECT orderID, custID, orderDate, status, totalPrice, paymentMethod FROM orders WHERE custID = %s ORDER BY orderDate DESC", (1,)
        )

    @patch('order_management.get_connection')
    def test_get_last_five_orders_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [ # Misal ada 3 order terakhir
            (105, 3, date(2024, 1, 20), 'Pending', 30000.0, 'Gopay'),
            (104, 1, date(2024, 1, 19), 'Shipped', 60000.0, 'OVO'),
            (103, 2, date(2024, 1, 18), 'Completed', 25000.0, 'Cash')
        ]
        expected_columns = ["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_last_five = get_last_five_orders()
        self.assertIsInstance(df_last_five, pd.DataFrame)
        self.assertEqual(len(df_last_five), 3) # Sesuai data mock
        self.assertListEqual(list(df_last_five.columns), expected_columns)
        mock_cursor.execute.assert_called_with(
            "SELECT orderID, custID, orderDate, status, totalPrice, paymentMethod FROM orders ORDER BY orderDate DESC LIMIT 5"
        )

    @patch('order_management.get_connection')
    def test_get_full_order_details_for_customer_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [ # List of dicts
            {'orderID': 101, 'bungaID': 1, 'bungaName': 'Rose', 'kuantitasTangkai': 5, 'custom': 'Pink', 
             'totalPrice': 50000.0, 'orderDate': date(2024,1,15), 'status': 'Completed', 'paymentMethod': 'Cash'}
        ]
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        details = get_full_order_details_for_customer(101, 1) # order_id, customer_id
        self.assertIsNotNone(details)
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]['bungaName'], 'Rose')
        mock_cursor.execute.assert_called_once() # Cek query dipanggil

    @patch('order_management.get_connection')
    def test_cancel_order_success(self, mock_get_conn):
        mock_cursor_check = MagicMock() # Cursor untuk SELECT status
        mock_cursor_check.fetchone.return_value = {'status': 'Pending'} # Order bisa dibatalkan

        mock_cursor_update = MagicMock() # Cursor untuk UPDATE status
        
        mock_conn_instance = MagicMock()
        # Atur agar pemanggilan cursor() yang berbeda mengembalikan mock cursor yang berbeda
        mock_conn_instance.cursor.side_effect = [
            MagicMock(__enter__=MagicMock(return_value=mock_cursor_check)),  # Untuk with conn.cursor(dictionary=True)
            MagicMock(__enter__=MagicMock(return_value=mock_cursor_update)) # Untuk with conn.cursor() saat update
        ]
        mock_get_conn.return_value = mock_conn_instance

        result = cancel_order(101, 1) # order_id, customer_id
        self.assertTrue(result["success"])
        self.assertIn("berhasil dibatalkan", result["message"])
        
        mock_cursor_check.execute.assert_called_with(
            "SELECT status FROM orders WHERE orderID = %s AND custID = %s", (101, 1)
        )
        mock_cursor_update.execute.assert_called_with(
            "UPDATE orders SET status = 'Cancelled' WHERE orderID = %s", (101,)
        )
        mock_conn_instance.commit.assert_called_once()

    @patch('order_management.get_connection')
    def test_cancel_order_already_completed(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'status': 'Completed'} # Order tidak bisa dibatalkan
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = cancel_order(102, 1)
        self.assertFalse(result["success"])
        self.assertIn("statusnya sudah 'Completed'", result["message"])
        self.assertFalse(mock_conn_instance.commit.called)


if __name__ == '__main__':
    unittest.main()