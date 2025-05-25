# product_management.py
import pandas as pd
from db_connection import get_connection
import mysql.connector

def get_all_products():
    conn = get_connection()
    try:
        # Menggunakan dictionary=True agar mudah diakses di UI
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT bungaID, bungaName, hargaPerTangkai, stock FROM products")
            return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error getting all products: {err}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

def update_stock(bungaID, tambahStock): # Diambil dari stock_logic.py Anda
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Panggil stored procedure UpdateProductStock
            # Pastikan stored procedure ini ada dan berfungsi dengan benar di MySQL
            cursor.callproc("UpdateProductStock", (bungaID, tambahStock))
            conn.commit()
            return True # Berhasil
    except mysql.connector.Error as err:
        print(f"Database error in update_stock: {err}")
        return False # Gagal
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_bunga_list():
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor: # dictionary=True untuk kemudahan akses
            query = "SELECT bungaID, bungaName FROM products"
            cursor.execute(query)
            return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error getting bunga list: {err}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_low_stock_products(threshold=5):
    conn = get_connection()
    try:
        with conn.cursor() as cursor: # Tidak pakai dictionary=True agar sesuai format kolom DataFrame
            query = "SELECT bungaName, stock FROM products WHERE stock <= %s ORDER BY stock ASC"
            cursor.execute(query, (threshold,))
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=["Nama Bunga", "Stok"])
    except mysql.connector.Error as err:
        print(f"Error getting low stock products: {err}")
        return pd.DataFrame()
    finally:
        if conn and conn.is_connected():
            conn.close()

def update_bunga_price(bungaID, new_price):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "UPDATE products SET hargaPerTangkai = %s WHERE bungaID = %s"
            cursor.execute(query, (new_price, bungaID))
            conn.commit()
            return True
    except mysql.connector.Error as err:
        print(f"Error updating bunga price: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_top_selling_products():
    conn = get_connection()
    try:
        with conn.cursor() as cursor: # Tidak pakai dictionary=True agar sesuai format kolom DataFrame
            query = """
            SELECT p.bungaName, SUM(od.kuantitasTangkai) AS total_terjual
            FROM orderdetails od
            JOIN products p ON od.bungaID = p.bungaID
            GROUP BY p.bungaName
            ORDER BY total_terjual DESC
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=["Nama Bunga", "Total Terjual"])
    except mysql.connector.Error as err:
        print(f"Error getting top selling products: {err}")
        return pd.DataFrame()
    finally:
        if conn and conn.is_connected():
            conn.close()