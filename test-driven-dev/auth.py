# auth.py
from db_connection import get_connection
import mysql.connector

def admin_login(username, password):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor: # dictionary=True agar hasil fetchone bisa diakses seperti dict
            query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = 'admin'"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            return result # Mengembalikan dict jika user ditemukan, None jika tidak
    except mysql.connector.Error as err:
        print(f"Error during admin login: {err}") # Sebaiknya log error
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def customer_login(username, password):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = 'customer'"
            cursor.execute(query, (username, password))
            return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error during customer login: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def extract_cust_id_from_username(username):
    cust_id = None
    if username and username.lower().startswith('customer'): # Tambah pengecekan username tidak None
        try:
            cust_id = int(username[8:])
        except ValueError:
            return None
    return cust_id

def verify_old_password(username, old_password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT password FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result and result[0] == old_password:
                return True
            return False
    except mysql.connector.Error as err:
        print(f"Error verifying old password: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def update_password(username, new_password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "UPDATE users SET password = %s WHERE username = %s"
            cursor.execute(query, (new_password, username))
            conn.commit()
            return True
    except mysql.connector.Error as err:
        print(f"Error updating password: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()