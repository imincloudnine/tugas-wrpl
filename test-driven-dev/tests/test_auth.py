# tests/test_auth.py
import unittest
from unittest.mock import patch, MagicMock
# import sys
# sys.path.append('../') # Jika auth.py ada di parent directory
from auth import admin_login, customer_login, extract_cust_id_from_username, verify_old_password, update_password
# Jangan lupa import mysql.connector jika ingin mock Error-nya secara spesifik
import mysql.connector


class TestAuth(unittest.TestCase):

    @patch('auth.get_connection') # Patch get_connection di dalam modul auth.py
    def test_admin_login_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        # Simulasikan admin ditemukan, perhatikan dictionary=True di fungsi aslinya
        mock_cursor.fetchone.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'} 
        
        mock_conn_instance = MagicMock()
        # Mengatur agar context manager (__enter__ dan __exit__) berfungsi dengan mock_cursor
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        user = admin_login('admin', 'password123')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'admin')
        # Pastikan query dieksekusi dengan parameter yang benar
        mock_cursor.execute.assert_called_with(
            "SELECT * FROM users WHERE username = %s AND password = %s AND role = 'admin'",
            ('admin', 'password123')
        )

    @patch('auth.get_connection')
    def test_admin_login_failure(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None # Simulasikan admin tidak ditemukan
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        user = admin_login('wrongadmin', 'wrongpass')
        self.assertIsNone(user)
    
    @patch('auth.get_connection')
    def test_admin_login_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        # Simulasikan error database saat eksekusi query
        mock_cursor.execute.side_effect = mysql.connector.Error("Database connection error")

        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        user = admin_login('admin', 'password')
        self.assertIsNone(user) # Fungsi harus mengembalikan None jika ada error DB

    def test_extract_cust_id_from_username(self):
        self.assertEqual(extract_cust_id_from_username("customer123"), 123)
        self.assertEqual(extract_cust_id_from_username("CUSTOMER456"), 456)
        self.assertIsNone(extract_cust_id_from_username("customerABC"))
        self.assertIsNone(extract_cust_id_from_username("cust123"))
        self.assertIsNone(extract_cust_id_from_username(None)) # Test untuk input None
        self.assertIsNone(extract_cust_id_from_username("")) # Test untuk input string kosong

    # Tambahkan test case untuk customer_login, verify_old_password, update_password
    # Mirip dengan test_admin_login, mock database call dan assert hasilnya.

if __name__ == '__main__':
    unittest.main()