# reporting.py
import pandas as pd
from db_connection import get_connection
import mysql.connector

def get_summary(): # Dari summary_logic.py Anda
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(totalPrice) FROM orders")
            total_income = cursor.fetchone()[0] or 0 # Jika NULL, jadi 0

            return total_customers, total_orders, total_income
    except mysql.connector.Error as err:
        print(f"Error getting summary: {err}")
        return 0, 0, 0 # Kembalikan nilai default jika error
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_monthly_revenue():
    conn = get_connection()
    try:
        with conn.cursor() as cursor: # Tidak pakai dictionary=True agar sesuai format kolom DataFrame
            # Pastikan sintaks DATE_FORMAT sesuai dengan MySQL
            query = """
                SELECT DATE_FORMAT(orderDate, '%Y-%m') AS month, SUM(totalPrice) AS revenue
                FROM orders
                GROUP BY month
                ORDER BY month
            """
            cursor.execute(query)
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=["Bulan", "Pendapatan"])
    except mysql.connector.Error as err:
        print(f"Error getting monthly revenue: {err}")
        return pd.DataFrame()
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_income_between_dates(start_date, end_date):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT SUM(totalPrice) AS total_income
            FROM orders
            WHERE DATE(orderDate) BETWEEN %s AND %s 
            """ # Menggunakan DATE() untuk memastikan perbandingan tanggal saja
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0
    except mysql.connector.Error as err:
        print(f"Error getting income between dates: {err}")
        return 0
    finally:
        if conn and conn.is_connected():
            conn.close()