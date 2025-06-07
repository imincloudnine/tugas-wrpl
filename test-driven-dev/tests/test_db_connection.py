import unittest
from unittest.mock import patch, MagicMock
import os
from db_connection import get_connection
import mysql.connector

class TestDbConnection(unittest.TestCase):

    @patch.dict(os.environ, {
        "DB_HOST": "tramway.proxy.rlwy.net",
        "DB_PORT": "3306",
        "DB_USER": "root",
        "DB_PASSWORD": "ZhFdrGfWRkSniHUZkVfxAuFWBSgiPdMw",
        "DB_NAME": "bouquetshop"
    })
    @patch('mysql.connector.connect')  # patch mysql connector connect
    def test_get_connection_success(self, mock_mysql_connect):
        mock_conn_instance = MagicMock()
        mock_mysql_connect.return_value = mock_conn_instance
        
        conn = get_connection()
        
        mock_mysql_connect.assert_called_once_with(
            host="tramway.proxy.rlwy.net",
            port=3306,
            user="root",
            password="ZhFdrGfWRkSniHUZkVfxAuFWBSgiPdMw",
            database="bouquetshop"
        )
        self.assertEqual(conn, mock_conn_instance)

    @patch.dict(os.environ, {
        "DB_HOST": "tramway.proxy.rlwy.net",
        "DB_PORT": "3306",
        "DB_USER": "root",
        "DB_PASSWORD": "ZhFdrGfWRkSniHUZkVfxAuFWBSgiPdMw",
        "DB_NAME": "bouquetshop"
    })
    @patch('mysql.connector.connect')
    def test_get_connection_failure(self, mock_mysql_connect):
        mock_mysql_connect.side_effect = mysql.connector.Error("Gagal terhubung")
        with self.assertRaises(mysql.connector.Error):
            get_connection()

if __name__ == '__main__':
    unittest.main()
