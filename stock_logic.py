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