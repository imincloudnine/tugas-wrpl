# order_management.py
import pandas as pd
from db_connection import get_connection
import mysql.connector

def create_new_order(custID, paymentMethod, bungaID, kuantitasTangkai, custom): # Dari order_logic.py Anda
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Panggil stored procedure CreateNewOrder
            # Pastikan stored procedure ini ada dan berfungsi di MySQL
            cursor.callproc("CreateNewOrder", (custID, paymentMethod, bungaID, kuantitasTangkai, custom))
            conn.commit()
            return {"success": True, "message": "Pesanan berhasil dibuat!"}
    except mysql.connector.Error as err:
        return {"success": False, "message": str(err)}
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_orders(search_query="", status="", order_date=None, payment_method=""): # Dari order_logic.py Anda
    conn = get_connection()
    try:
        # Nama kolom harus sesuai dengan urutan SELECT untuk pd.DataFrame
        column_names = ["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"]
        with conn.cursor() as cursor: # Tidak pakai dictionary=True agar urutan kolom terjaga untuk DataFrame
            query = "SELECT orderID, custID, orderDate, status, totalPrice, paymentMethod FROM orders WHERE orderID LIKE %s"
            params = [f"%{search_query}%"]
            if status:
                query += " AND status = %s"
                params.append(status)
            if order_date: # order_date harus berupa string 'YYYY-MM-DD' atau objek date
                query += " AND DATE(orderDate) = %s"
                params.append(order_date)
            if payment_method:
                query += " AND paymentMethod = %s"
                params.append(payment_method)
            
            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=column_names)
    except mysql.connector.Error as err:
        print(f"Error getting orders: {err}")
        return pd.DataFrame(columns=column_names) # Kembalikan DataFrame kosong jika error
    finally:
        if conn and conn.is_connected():
            conn.close()


def update_order_status(orderID, newStatus):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Panggil stored procedure UpdateOrderStatus
            # Pastikan stored procedure ini ada dan berfungsi di MySQL
            cursor.callproc("UpdateOrderStatus", (orderID, newStatus))
            conn.commit()
            return True
    except mysql.connector.Error as err:
        print(f"Error updating order status: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_order_details_table(search_query="", search_orderID="", bungaID="", kuantitasTangkai="", custom=""):
    conn = get_connection()
    try:
        # Nama kolom harus sesuai dengan urutan SELECT untuk pd.DataFrame
        column_names = ["Order Details ID", "Order ID", "Bunga ID", "Kuantitas Tangkai", "Harga Unit", "Custom"]
        with conn.cursor() as cursor: # Tidak pakai dictionary=True agar urutan kolom terjaga untuk DataFrame
            query = "SELECT orderDetailsID, orderID, bungaID, kuantitasTangkai, hargaUnit, custom FROM orderdetails WHERE 1=1" # hargaUnit diambil dari tabel
            params = []

            if search_query: # Asumsi search_query adalah untuk orderDetailsID
                query += " AND orderDetailsID = %s"
                params.append(search_query)
            if search_orderID:
                query += " AND orderID = %s"
                params.append(search_orderID)
            if bungaID:
                query += " AND bungaID = %s"
                params.append(bungaID)
            if kuantitasTangkai:
                query += " AND kuantitasTangkai = %s"
                params.append(kuantitasTangkai)
            if custom:
                query += " AND custom LIKE %s" # Menggunakan LIKE untuk custom
                params.append(f"%{custom}%")

            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=column_names)
    except mysql.connector.Error as err:
        print(f"Error getting order details table: {err}")
        return pd.DataFrame(columns=column_names)
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_customer_orders_history(custID): # Mengganti nama dari get_customer_orders agar lebih jelas
    conn = get_connection()
    try:
        # Nama kolom harus sesuai dengan urutan SELECT untuk pd.DataFrame
        column_names = ["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"]
        with conn.cursor() as cursor: # Tidak pakai dictionary=True
            query = "SELECT orderID, custID, orderDate, status, totalPrice, paymentMethod FROM orders WHERE custID = %s ORDER BY orderDate DESC"
            cursor.execute(query, (custID,))
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=column_names)
    except mysql.connector.Error as err:
        print(f"Error getting customer orders history: {err}")
        return pd.DataFrame(columns=column_names)
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_last_five_orders():
    conn = get_connection()
    try:
        # Nama kolom harus sesuai dengan urutan SELECT untuk pd.DataFrame
        column_names = ["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"]
        with conn.cursor() as cursor: # Tidak pakai dictionary=True
            query = "SELECT orderID, custID, orderDate, status, totalPrice, paymentMethod FROM orders ORDER BY orderDate DESC LIMIT 5"
            cursor.execute(query)
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=column_names)
    except mysql.connector.Error as err:
        print(f"Error getting last five orders: {err}")
        return pd.DataFrame(columns=column_names)
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_full_order_details_for_customer(order_id, customer_id):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor: # dictionary=True untuk UI component
            query = """
            SELECT 
                od.orderID, od.bungaID, p.bungaName, od.kuantitasTangkai,
                od.custom, o.totalPrice, o.orderDate, o.status, o.paymentMethod
            FROM orderdetails od
            JOIN orders o ON od.orderID = o.orderID
            JOIN products p ON od.bungaID = p.bungaID
            WHERE od.orderID = %s AND o.custID = %s
            """
            cursor.execute(query, (order_id, customer_id))
            return cursor.fetchall() # Akan menjadi list of dicts
    except mysql.connector.Error as err:
        print(f"Error fetching full order details for customer: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def cancel_order(order_id, customer_id):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor: # dictionary=True untuk membaca status
            check_query = "SELECT status FROM orders WHERE orderID = %s AND custID = %s"
            cursor.execute(check_query, (order_id, customer_id))
            result = cursor.fetchone()

            if not result:
                return {"success": False, "message": "Order tidak ditemukan atau bukan milik Anda."}

            current_status = result['status']
            if current_status in ("Completed", "Shipped", "Cancelled"):
                return {"success": False, "message": f"Pesanan tidak bisa dibatalkan karena statusnya sudah '{current_status}'."}

            update_query = "UPDATE orders SET status = 'Cancelled' WHERE orderID = %s"
            # Buka cursor baru tanpa dictionary=True untuk operasi update jika perlu, atau pastikan cursor bisa dipakai ulang
            with conn.cursor() as update_cursor:
                 update_cursor.execute(update_query, (order_id,))
                 conn.commit()
            return {"success": True, "message": f"Pesanan {order_id} berhasil dibatalkan."}
    except mysql.connector.Error as err:
        return {"success": False, "message": str(err)}
    finally:
        if conn and conn.is_connected():
            conn.close()