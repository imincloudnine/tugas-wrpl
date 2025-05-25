# tests/test_customer_management.py
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
sys.path.append('../')
from customer_management import add_customer, get_customers, delete_customer, get_customer_info
import mysql.connector

class TestCustomerManagement(unittest.TestCase):

    @patch('customer_management.get_connection')
    def test_add_customer_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        # Mock untuk SELECT last_userID
        mock_cursor.fetchone.return_value = (101,) # Misal customer_id baru adalah 101
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = add_customer("John", "Doe", "john.doe@example.com", "12345", "123 Main St", "password123")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["username"], "customer101")
        
        # Cek pemanggilan stored procedure AddCustomer
        mock_cursor.callproc.assert_any_call("AddCustomer", ("John", "Doe", "john.doe@example.com", "12345", "123 Main St"))
        # Cek SELECT last_userID
        mock_cursor.execute.assert_any_call("SELECT last_userID as customer_id FROM usersequence WHERE id = 1")
        # Cek INSERT ke tabel users
        mock_cursor.execute.assert_any_call(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            ("customer101", "password123", "customer")
        )
        self.assertEqual(mock_conn_instance.commit.call_count, 2) # Dua kali commit

    @patch('customer_management.get_connection')
    def test_add_customer_failure_no_userid(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None # Gagal mendapatkan last_userID
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = add_customer("Jane", "Doe", "jane.doe@example.com", "67890", "456 Oak St", "securepass")
        self.assertFalse(result["success"])
        self.assertIn("Gagal mendapatkan ID customer baru", result["message"])

    @patch('customer_management.get_connection')
    def test_add_customer_db_error_on_callproc(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.callproc.side_effect = mysql.connector.Error("Error calling procedure")
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = add_customer("Jim", "Beam", "jim.beam@example.com", "11223", "789 Pine St", "strongpass")
        self.assertFalse(result["success"])
        self.assertTrue("Error calling procedure" in result["message"])


    @patch('customer_management.get_connection')
    def test_get_customers_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, 'John', 'Doe', 'john@example.com', '12345', 'Address 1'),
            (2, 'Jane', 'Doe', 'jane@example.com', '67890', 'Address 2')
        ]
        expected_columns = ["Customer ID", "First Name", "Last Name", "Email", "Phone Number", "Address"]
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_customers = get_customers(search_query="Doe")
        
        self.assertIsInstance(df_customers, pd.DataFrame)
        self.assertEqual(len(df_customers), 2)
        self.assertListEqual(list(df_customers.columns), expected_columns)
        mock_cursor.execute.assert_called_once() # Cek bahwa execute dipanggil

    @patch('customer_management.get_connection')
    def test_get_customers_not_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [] # Tidak ada customer ditemukan
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        df_customers = get_customers(search_query="NonExistent")
        self.assertTrue(df_customers.empty)

    @patch('customer_management.get_connection')
    def test_get_customers_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB error")

        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        df_customers = get_customers(search_query="test")
        self.assertTrue(df_customers.empty) # Harusnya mengembalikan DataFrame kosong


    @patch('customer_management.get_connection')
    def test_delete_customer_success(self, mock_get_conn):
        mock_cursor = MagicMock()
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        cust_id_to_delete = 10
        result = delete_customer(cust_id_to_delete)
        
        self.assertTrue(result["success"])
        self.assertIn(f"Customer ID {cust_id_to_delete} dan user 'customer{cust_id_to_delete}' berhasil dihapus!", result["message"])
        mock_cursor.callproc.assert_called_with("DeleteCustomer", (cust_id_to_delete,))
        mock_cursor.execute.assert_called_with("DELETE FROM users WHERE username = %s", (f"customer{cust_id_to_delete}",))
        self.assertEqual(mock_conn_instance.commit.call_count, 2)

    @patch('customer_management.get_connection')
    def test_delete_customer_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.callproc.side_effect = mysql.connector.Error("Error deleting customer")
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        result = delete_customer(20)
        self.assertFalse(result["success"])
        self.assertIn("Error deleting customer", result["message"])

    @patch('customer_management.get_connection')
    def test_get_customer_info_found_with_user(self, mock_get_conn):
        mock_cursor = MagicMock()
        # dictionary=True, jadi fetchone mengembalikan dict
        mock_cursor.fetchone.side_effect = [
            {'firstName': 'Test', 'lastName': 'User', 'email': 'test@user.com', 'phoneNumber': '000', 'address': 'Addr'}, # Info customer
            {'username': 'customer1', 'password': 'pwd'} # Info user (password sebaiknya tidak diambil jika tidak perlu)
        ]
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        info = get_customer_info(1)
        self.assertIsNotNone(info)
        self.assertEqual(info['firstName'], 'Test')
        self.assertEqual(info['username'], 'customer1')
        
        # Cek query yang dipanggil
        mock_cursor.execute.assert_any_call("SELECT firstName, lastName, email, phoneNumber, address FROM customers WHERE custID = %s", (1,))
        mock_cursor.execute.assert_any_call("SELECT username, password FROM users WHERE username = %s", ('customer1',))

    @patch('customer_management.get_connection')
    def test_get_customer_info_customer_not_found(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None # Customer info not found
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance

        info = get_customer_info(999)
        self.assertIsNone(info)

    @patch('customer_management.get_connection')
    def test_get_customer_info_db_error(self, mock_get_conn):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB error")

        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn_instance
        
        info = get_customer_info(1)
        self.assertIsNone(info)

if __name__ == '__main__':
    unittest.main()