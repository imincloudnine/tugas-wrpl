# customer_management.py
import pandas as pd
from db_connection import get_connection
import mysql.connector

def add_customer(first_name, last_name, email, phone_number, address, password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("AddCustomer", (first_name, last_name, email, phone_number, address))
            conn.commit() # Commit setelah AddCustomer

            # Ambil customer_id yang baru dibuat
            cursor.execute("SELECT last_userID as customer_id FROM usersequence WHERE id = 1") # Pastikan tabel dan kolom ini ada
            result = cursor.fetchone()
            if not result:
                return {"success": False, "message": "Gagal mendapatkan ID customer baru."}
            customer_id = result[0]
            username = f"customer{customer_id}"

            # Insert ke tabel users
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, "customer")
            )
            conn.commit() # Commit setelah insert user
            return {"success": True, "username": username, "message": f"Customer berhasil dibuat! Username Anda: {username}"}
    except mysql.connector.Error as err:
        return {"success": False, "message": str(err)}
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_customers(search_query="", custid=""):
    conn = get_connection()
    try:
        with conn.cursor() as cursor: # Tidak pakai dictionary=True agar sesuai dengan format kolom DataFrame
            query = "SELECT custID, firstName, lastName, email, phoneNumber, address FROM customers WHERE (firstName LIKE %s OR lastName LIKE %s OR email LIKE %s)"
            params = [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"]
            if custid:
                query += " AND custID = %s"
                params.append(custid)
            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
            # Nama kolom harus sesuai dengan urutan SELECT
            return pd.DataFrame(result, columns=["Customer ID", "First Name", "Last Name", "Email", "Phone Number", "Address"])
    except mysql.connector.Error as err:
        print(f"Error getting customers: {err}")
        return pd.DataFrame() # Kembalikan DataFrame kosong jika error
    finally:
        if conn and conn.is_connected():
            conn.close()

def delete_customer(custID):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Hapus dari tabel customers (via stored procedure)
            cursor.callproc("DeleteCustomer", (custID,))
            conn.commit()

            # Hapus dari tabel users
            username = f"customer{custID}"
            delete_user_query = "DELETE FROM users WHERE username = %s"
            cursor.execute(delete_user_query, (username,))
            conn.commit()
            return {"success": True, "message": f"Customer ID {custID} dan user '{username}' berhasil dihapus!"}
    except mysql.connector.Error as err:
        return {"success": False, "message": str(err)}
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_customer_info(custID):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            query_cust = "SELECT firstName, lastName, email, phoneNumber, address FROM customers WHERE custID = %s"
            cursor.execute(query_cust, (custID,))
            customer_info = cursor.fetchone()
            
            if not customer_info:
                return None # Customer tidak ditemukan

            username = f"customer{custID}"
            query_user = "SELECT username, password FROM users WHERE username = %s" # Password sebaiknya tidak diambil kecuali sangat perlu
            cursor.execute(query_user, (username,))
            user_info = cursor.fetchone()
            
            if user_info: # Gabungkan jika keduanya ada
                return {**customer_info, **user_info}
            return customer_info # Kembalikan info customer saja jika user tidak terkait (jarang terjadi jika data konsisten)
    except mysql.connector.Error as err:
        print(f"Error getting customer info: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()