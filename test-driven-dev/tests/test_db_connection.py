# tests/test_db_connection.py
import unittest
from unittest.mock import patch, MagicMock
# Pastikan db_connection.py bisa diimpor. Mungkin perlu mengatur PYTHONPATH
# atau struktur proyek agar Python menemukannya.
# Jika tests/ sejajar dengan db_connection.py, Anda mungkin perlu:
# import sys
# sys.path.append('../') # Tambahkan parent directory ke path
from db_connection import get_connection
import mysql.connector

class TestDbConnection(unittest.TestCase):
    @patch('mysql.connector.connect') # Patch object yang akan dipanggil
    def test_get_connection_success(self, mock_mysql_connect):
        # Atur apa yang dikembalikan oleh mock
        mock_conn_instance = MagicMock()
        mock_mysql_connect.return_value = mock_conn_instance
        
        conn = get_connection()
        
        # Verifikasi bahwa mysql.connector.connect dipanggil dengan argumen yang benar
        mock_mysql_connect.assert_called_once_with(
            host="localhost", # Sesuaikan dengan konfigurasi Anda
            user="root",
            password="",
            database="bshop"
        )
        self.assertEqual(conn, mock_conn_instance) # Pastikan objek koneksi yang dikembalikan adalah mock kita

    @patch('mysql.connector.connect')
    def test_get_connection_failure(self, mock_mysql_connect):
        # Simulasikan error saat koneksi
        mock_mysql_connect.side_effect = mysql.connector.Error("Gagal terhubung")
        
        # Pastikan error yang diharapkan muncul
        with self.assertRaises(mysql.connector.Error):
            get_connection()

if __name__ == '__main__':
    unittest.main()