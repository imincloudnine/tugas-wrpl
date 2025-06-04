import mysql.connector
import pandas as pd
from db_connection import get_connection  # pastikan ini ada

# Fungsi untuk memperbarui stok produk
def update_stock(bungaID, tambahStock):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("UpdateProductStock", (bungaID, tambahStock))
            conn.commit()
            return True
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return False
    finally:
        conn.close()

# Fungsi untuk mengambil stok produk berdasarkan bungaID
def get_stock_level(bungaID):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT stock FROM products WHERE bungaID = %s"
            cursor.execute(query, (bungaID,))
            result = cursor.fetchone()
            return result[0] if result else 0
    except mysql.connector.Error as err:
        print(f"Error getting stock level: {err}")
        return 0
    finally:
        conn.close()
