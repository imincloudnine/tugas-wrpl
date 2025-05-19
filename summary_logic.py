import mysql.connector
from db_connection import get_connection

def get_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(totalPrice) FROM orders")
            total_income = cursor.fetchone()[0] or 0

            return total_customers, total_orders, total_income
    finally:
        conn.close()
