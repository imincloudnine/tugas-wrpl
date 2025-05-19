import mysql.connector
import pandas as pd
from db_connection import get_connection  # pastikan ini ada

def create_new_order(custID, paymentMethod, bungaID, kuantitasTangkai, custom):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("CreateNewOrder", (custID, paymentMethod, bungaID, kuantitasTangkai, custom))
            conn.commit()
            return {"success": True, "message": "Pesanan berhasil dibuat!"}
    except mysql.connector.Error as err:
        return {"success": False, "message": str(err)}
    finally:
        conn.close()

def get_orders(search_query="", status="", order_date="", payment_method=""):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM orders WHERE orderID LIKE %s"
            params = [f"%{search_query}%"]
            if status:
                query += " AND status = %s"
                params.append(status)
            if order_date:
                query += " AND DATE(orderDate) = %s"
                params.append(order_date)
            if payment_method:
                query += " AND paymentMethod = %s"
                params.append(payment_method)
            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
            return result  # return raw data, biar bebas mau jadi df atau dict di UI
    finally:
        conn.close()
