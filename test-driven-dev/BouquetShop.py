import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import io
from order_logic import create_new_order, get_orders
import pandas as pd
from summary_logic import get_summary

# Styling
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .product-card {
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 15px;
            margin-bottom: 20px;
            background: white;
            transition: transform 0.2s;
        }
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .header {
            background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #fdfbfb 0%, #ebedee 100%);
        }
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .btn-primary {
            background-color: #ff6b6b;
            color: #e75480;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            cursor: pointer;
        }
        .btn-primary:hover {
            background-color: #ff5252;
        }
        input[type="text"], input[type="number"] {
            color: #e75480 !important;
            border: 1px solid #ddd !important;
            border-radius: 8px !important;
            padding: 6.25px !important;
            border-top: 1px solid #ddd !important;
        }
        .stSelectbox > div > div {
            color: #e75480 !important;
            border: 1px solid #ddd !important;
            border-radius: 6px !important;
        }
        .stSelectbox div[data-baseweb="select"] {
            color: #e75480 !important;
            border-radius: 6px !important;
        }
        input[type="text"]:focus, input[type="number"]:focus {
            border-color: #888 !important;
            outline: none !important;
        }
        .stSelectbox div[data-baseweb="select"]:hover {
            border-color: #888 !important;
        }
        .stNumberInput button:hover {
            background-color: #ddd !important;
        }
        .stNumberInput {
            border-radius: 6px !important;
        }
        textarea {
            color: white !important;
            border: 1px solid #ddd !important;
            border-radius: 8px !important;
            padding: 6.25px !important;
            border-top: 1px solid #ddd !important;
        }
        textarea:focus {
            border-color: #888 !important;
            outline: none !important;
        }
        input[type="password"] {
            color: #e75480 !important;
            border: 1px solid #ddd !important;
            border-radius: 8px !important;
            padding: 6.25px !important;
            border-top: 1px solid #ddd !important;
        }
        input[type="password"]:focus {
            border-color: #888 !important;
            outline: none !important;
        }
            
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 10px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            min-height: 100px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }
        
        .metric-card h3 {
            font-size: 14px !important;
            margin-bottom: 8px !important;
            color: #666 !important;
        }
        
        .metric-card h2 {
            font-size: 18px !important;
            font-weight: bold !important;
            color: #ff6b6b !important;
            margin: 0 !important;
        }
        
        .metric-card div[style*="font-size:2em"] {
            font-size: 20px !important;
            margin-bottom: 5px !important;
        }    
    </style>
""", unsafe_allow_html=True)


import psycopg2
import os  # Untuk membaca environment variables (jika digunakan)

def get_connection():
    return psycopg2.connect(
        host="kfagkljzyfdegjomntoy.supabase.co",  # Dari NEXT_PUBLIC_SUPABASE_URL (tanpa https://)
        port=5432,
        database="postgres",  # Ganti jika berbeda
        user="imincloudnine",      # Ganti dengan user yang benar
        password="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtmYWdrbGp6eWZkZWdqb21udG95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwMDkwMDIsImV4cCI6MjA2MzU4NTAwMn0.Pd4MPHRuOy0M9lOIUxw3EHP27SdPmVYVa_niz77xLJE"  # Ganti dengan password yang benar
        # Atau, lebih baik: password=os.environ.get("SUPABASE_DB_PASSWORD")
    )

# Header
def show_header(title):
    st.markdown(f"""
        <div class="header">
            <h1 style="margin:0; display:flex; align-items:center;">
                <span style="margin-right:10px;">💐</span>
                {title}
            </h1>
        </div>
    """, unsafe_allow_html=True)

# Fungsi untuk menampilkan produk dalam card
def display_product_card(product):
    col1, col2 = st.columns([1, 3])
    with col1:
        try:
            # Asumsikan product[0] adalah ID produk (1, 2, 3, dst)
            st.image(f"images/{product[0]}.jpg", width=150)
        except:
            st.image("https://via.placeholder.com/150x150.png?text=Bouquet", width=150)

    with col2:
        st.subheader(product[1])
        st.markdown(f"**Harga:** Rp {product[2]:,.2f} per tangkai")
        st.markdown(f"**Stok tersedia:** {product[3]} tangkai")
        st.markdown(f"**ID Produk:** {product[0]}")
        
        if st.session_state.role == "customer":
            with st.expander("Buat Pesanan"):
                with st.form(key=f"order_form_{product[0]}"):
                    paymentMethod = st.selectbox("Metode Pembayaran", ["Cash", "OVO", "Gopay", "Dana"], key=f"pay_{product[0]}")
                    kuantitasTangkai = st.number_input("Jumlah Tangkai", min_value=1, max_value=10, step=1, key=f"qty_{product[0]}")
                    custom = st.selectbox("Warna Custom", ["Pink", "Brown", "Blue", "Green", "Grey", "Yellow", "White", "Purple"], key=f"custom_{product[0]}")
                    
                    if st.form_submit_button("Pesan Sekarang", type="primary"):
                        username = st.session_state.username
                        custID = extract_cust_id_from_username(username)
                        if custID:
                            create_new_order(custID, paymentMethod, product[0], kuantitasTangkai, custom)
                        else:
                            st.error("Gagal membuat pesanan. Silakan login kembali.")

# Fungsi untuk menampilkan produk dalam grid
def display_products_grid():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products")
            product_list = cursor.fetchall()

            cols = st.columns(3)
            for idx, product in enumerate(product_list):
                with cols[idx % 3]:
                    try:
                        st.image(f"images/{product[0]}.jpg", use_container_width=True)
                    except:
                        st.image("https://via.placeholder.com/200x200.png?text=Bouquet", use_container_width=True)
                    st.write(f"**{product[1]}**")
                    st.write(f"Rp {product[2]:,.2f}")
                    st.write(f"Stok: {product[3]} tangkai")
                    
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")

# Fungsi untuk menampilkan metrik dalam card
def display_metric_card(title, value, icon="📊"):
    st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:2em; margin-bottom:10px;">{icon}</div>
            <h3>{title}</h3>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)

# Login
def admin_login(username, password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = 'admin'"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            if result:
                user_info = {
                    "id": result[0],
                    "username": result[1],
                    "password": result[2],
                    "role": result[3]
                }
                return user_info
            return None
    finally:
        conn.close()

def customer_login(username, password):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = 'customer'"
            cursor.execute(query, (username, password))
            return cursor.fetchone()
    finally:
        conn.close()

# Fungsi untuk mengekstrak custID dari username
def extract_cust_id_from_username(username):
    cust_id = None
    if username.lower().startswith('customer'):
        try:
            cust_id = int(username[8:])
        except ValueError:
            return None
    return cust_id

# Fungsi untuk menambah customer
def add_customer(first_name, last_name, email, phone_number, address, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.callproc("AddCustomer", (first_name, last_name, email, phone_number, address))
        conn.commit()

        cursor.execute("SELECT last_userID as customer_id FROM usersequence WHERE id = 1")
        result = cursor.fetchone()
        customer_id = result[0]

        username = f"customer{customer_id}"

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, "customer")
        )
        conn.commit()

        st.success(f"Customer berhasil dibuat! Username Anda: {username}")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        conn.close()


# Fungsi untuk membuat pesanan baru
#def create_new_order(custID, paymentMethod, bungaID, kuantitasTangkai, custom):
 #   conn = get_connection()
  #  try:
   #     with conn.cursor() as cursor:
    #        cursor.callproc("CreateNewOrder", (custID, paymentMethod, bungaID, kuantitasTangkai, custom))
     #       conn.commit()
      #      st.success("Pesanan berhasil dibuat!")
   # except mysql.connector.Error as err:
    #    st.error(f"Error: {err}")
   # finally:
    #    conn.close()

# Fungsi untuk memperbarui status pesanan
def update_order_status(orderID, newStatus):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("UpdateOrderStatus", (orderID, newStatus))
            conn.commit()
            return True
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return False
    finally:
        conn.close()

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

# Fungsi untuk mengambil data produk terlaris
def get_top_selling_products():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
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
    finally:
        conn.close()

# Fungsi untuk mengambil data customer
def get_customers(search_query="", custid=""):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM customers WHERE (firstName LIKE %s OR lastName LIKE %s OR email LIKE %s)"
            params = [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"]
            if custid:
                query += " AND custID = %s"
                params.append(custid)
            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=["Customer ID", "First Name", "Last Name", "Email", "Phone Number", "Address"])
    finally:
        conn.close()

# Fungsi untuk mengambil data orders
#def get_orders(search_query="", status="", order_date="", payment_method=""):
 #   conn = get_connection()
  #  try:
   #     with conn.cursor() as cursor:
    #        query = "SELECT * FROM orders WHERE orderID LIKE %s"
     #       params = [f"%{search_query}%"]
      #      if status:
       #         query += " AND status = %s"
        #        params.append(status)
         #   if order_date:
          #      query += " AND DATE(orderDate) = %s"
           #     params.append(order_date)
            #if payment_method:
             #   query += " AND paymentMethod = %s"
              #  params.append(payment_method)
           # cursor.execute(query, tuple(params))
           # result = cursor.fetchall()
           # return pd.DataFrame(result, columns=["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"])
   # finally:
    #    conn.close()

# Fungsi untuk mengambil data order details
def get_order_details(search_query="", search_orderID="", bungaID="", kuantitasTangkai="", custom=""):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM orderdetails WHERE 1=1"
            params = []

            if search_query:
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
                query += " AND custom = %s"
                params.append(custom)

            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=["Order Details ID", "Order ID", "Bunga ID", "Kuantitas Tangkai", "Harga Unit", "Custom"])
    finally:
        conn.close()

# Fungsi untuk mengambil data pendapatan bulanan
def get_monthly_revenue():
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT DATE_FORMAT(orderdate, '%Y-%m') AS month, SUM(totalprice) AS revenue
        FROM orders
        GROUP BY month
        ORDER BY month
    """
    
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return pd.DataFrame(data, columns=["Bulan", "Pendapatan"])

# Fungsi Hapus Customer
def delete_customer(custID):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("DeleteCustomer", (custID,))
            conn.commit()

            username = f"customer{custID}"
            delete_user_query = "DELETE FROM users WHERE username = %s"
            cursor.execute(delete_user_query, (username,))
            conn.commit()

            st.success(f"Customer ID {custID} dan user '{username}' berhasil dihapus!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        conn.close()

# Riwayat Pesanan Customer
def get_customer_orders(custID):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM orders WHERE custID = %s ORDER BY orderDate DESC"
            cursor.execute(query, (custID,))
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"])
    finally:
        conn.close()

# 5 Pesanan Terakhir
def get_last_five_orders():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM orders ORDER BY orderDate DESC LIMIT 5"
            cursor.execute(query)
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"])
    finally:
        conn.close()

# Stok Bunga Rendah
def get_low_stock_products(threshold=5):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT bungaName, stock FROM products WHERE stock <= %s ORDER BY stock ASC"
            cursor.execute(query, (threshold,))
            result = cursor.fetchall()
            return pd.DataFrame(result, columns=["Nama Bunga", "Stok"])
    finally:
        conn.close()

# Update Harga Bunga
def update_bunga_price(bungaID, new_price):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "UPDATE products SET hargaPerTangkai = %s WHERE bungaID = %s"
            cursor.execute(query, (new_price, bungaID))
            conn.commit()
            return True
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return False
    finally:
        conn.close()

# Pendapatan Berdasarkan Tanggal
def get_income_between_dates(start_date, end_date):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT SUM(totalPrice) AS total_income
            FROM orders
            WHERE orderDate BETWEEN %s AND %s
            """
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
    finally:
        conn.close()

# Fungsi ambil data customer dari database
def get_customer_info(custID):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            query_cust = "SELECT firstName, lastName, email, phoneNumber, address FROM customers WHERE custID = %s"
            cursor.execute(query_cust, (custID,))
            customer_info = cursor.fetchone()
            
            username = f"customer{custID}"
            query_user = "SELECT username, password FROM users WHERE username = %s"
            cursor.execute(query_user, (username,))
            user_info = cursor.fetchone()
            
            if customer_info and user_info:
                return {**customer_info, **user_info}
            else:
                return None
    finally:
        conn.close()

# Fungsi untuk memverifikasi password lama
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
    finally:
        conn.close()

# Fungsi untuk mengupdate password baru
def update_password(username, new_password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "UPDATE users SET password = %s WHERE username = %s"
            cursor.execute(query, (new_password, username))
            conn.commit()
            return True
    except mysql.connector.Error as err:
        return False
    finally:
        conn.close()

# Dashboard
get_summary()
#def get_summary():
 #   conn = get_connection()
  #  try:
   #     with conn.cursor() as cursor:
    #        cursor.execute("SELECT COUNT(*) FROM customers")
     #       total_customers = cursor.fetchone()[0]

      #      cursor.execute("SELECT COUNT(*) FROM orders")
       #     total_orders = cursor.fetchone()[0]

        #    cursor.execute("SELECT SUM(totalPrice) FROM orders")
         #   total_income = cursor.fetchone()[0] or 0

          #  return total_customers, total_orders, total_income
   # finally:
    #    conn.close()

# Fungsi untuk mendapatkan nama bunga
def get_bunga_list():
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT bungaID, bungaName FROM products"
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        conn.close()

# Detail Pesanan
def show_order_details(order_id, customer_id):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
            SELECT 
                od.orderID,
                od.bungaID,
                p.bungaName,
                od.kuantitasTangkai,
                od.custom,
                o.totalPrice,
                o.orderDate,
                o.status,
                o.paymentMethod
            FROM orderdetails od
            JOIN orders o ON od.orderID = o.orderID
            JOIN products p ON od.bungaID = p.bungaID
            WHERE od.orderID = %s AND o.custID = %s
            """
            cursor.execute(query, (order_id, customer_id))
            details = cursor.fetchall()

            if not details:
                st.error("Pesanan tidak ditemukan atau bukan milik Customer.")
            else:
                st.subheader(f"Detail Pesanan (Order ID: {order_id})")
                st.write(f"**Tanggal Pesanan:** {details[0]['orderDate']}")
                st.write(f"**Metode Pembayaran:** {details[0]['paymentMethod']}")
                st.write(f"**Status:** {details[0]['status']}")

                st.markdown("---")
                st.write("**Daftar Item Pesanan:**")

                for item in details:
                    st.write(f"- **Nama Bunga:** {item['bungaName']}")
                    st.write(f"  - Jumlah Tangkai: {item['kuantitasTangkai']}")
                    st.write(f"  - Custom: {item['custom']}")
                    st.write(f"  - Harga Total Item: Rp {item['totalPrice']:,}")
                    st.markdown("---")

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        conn.close()

# Batalkan Pesanan
def cancel_order(order_id, customer_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Cek apakah order milik customer dan statusnya masih boleh dibatalkan
            check_query = """
            SELECT status FROM orders 
            WHERE orderID = %s AND custID = %s
            """
            cursor.execute(check_query, (order_id, customer_id))
            result = cursor.fetchone()

            if not result:
                st.error("Order tidak ditemukan atau bukan milik Anda.")
                return

            current_status = result[0]
            if current_status in ("Completed", "Shipped", "Cancelled"):
                st.warning(f"Pesanan tidak bisa dibatalkan karena statusnya sudah '{current_status}'.")
                return

            # Update status menjadi cancelled
            update_query = """
            UPDATE orders 
            SET status = 'Cancelled'
            WHERE orderID = %s
            """
            cursor.execute(update_query, (order_id,))
            conn.commit()
            st.success(f"Pesanan {order_id} berhasil dibatalkan.")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        conn.close()

# Inisialisasi session_state
if "role" not in st.session_state:
    st.session_state.role = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "username" not in st.session_state:
    st.session_state.username = None

# Halaman Login/Signup
if st.session_state.role is None:
    show_header("Bouquet Shop")
    
    pilihan_awal = st.radio("Silakan pilih", ("Login", "Sign Up"), horizontal=True)
    
    if pilihan_awal == "Login":
        role = st.radio("Login sebagai", ("Admin", "Customer"), horizontal=True)
        
        if role == "Admin":
            with st.form(key="admin_login_form"):
                st.subheader("Login Admin")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", type="primary"):
                    user = admin_login(username, password)
                    if user:
                        st.success(f"Selamat datang, Admin!")
                        st.session_state.role = "admin"
                        st.session_state.user_info = user
                        st.rerun()
                    else:
                        st.error("Username atau password salah!")

        elif role == "Customer":
            with st.form(key="customer_login_form"):
                st.subheader("Login Customer")
                username = st.text_input("Username (Format: customerID)")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", type="primary"):
                    user = customer_login(username, password)
                    if user:
                        st.success(f"Selamat datang, Customer!") 
                        st.session_state.role = "customer"
                        st.session_state.user_info = user
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Username atau password salah!")

    elif pilihan_awal == "Sign Up":
        with st.form(key="signup_form"):
            st.subheader("Daftar Akun Customer Baru")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("Nama Depan")
            with col2:
                last_name = st.text_input("Nama Belakang")
            email = st.text_input("Email")
            phone_number = st.text_input("Nomor Telepon")
            address = st.text_area("Alamat")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Daftar Sekarang", type="primary"):
                if first_name and last_name and email and phone_number and address and password:
                    add_customer(first_name, last_name, email, phone_number, address, password)
                else:
                    st.error("Semua kolom harus diisi!")
    st.stop()

# Sidebar Navigation
st.sidebar.title("💐 Bouquet Shop")

if st.session_state.role == 'admin':
    st.sidebar.markdown(f"**Halo, Admin!**")
    page = st.sidebar.radio("Menu", [
        "Beranda", "Produk", "Pelanggan", "Pesanan", 
        "Laporan Penjualan"
    ])
elif st.session_state.user_info['role'] == 'customer':
    st.sidebar.markdown(f"**Halo, Customer!**")
    page = st.sidebar.radio("Menu", [
        "Beranda", "Produk", "Pesanan", "Informasi Akun"
    ])

if st.sidebar.button("🚪 Logout"):
    st.session_state.role = None
    st.session_state.user_info = None
    st.session_state.username = None
    st.rerun()

# Halaman Admin
if st.session_state.role == 'admin':
    if page == "Beranda":
        show_header("Beranda")
        
        customers, orders, income = get_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            display_metric_card("Total Pelanggan", customers, "👥")
        with col2:
            display_metric_card("Total Pesanan", orders, "📦")
        with col3:
            display_metric_card("Total Pendapatan", f"Rp{int(income):,}", "💰")
        
        st.subheader("5 Pesanan Terbaru")
        df = get_last_five_orders()
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("Belum ada pesanan.")
        
        st.subheader("Produk dengan Stok Rendah")
        threshold = st.number_input("Batas Stok Minimum", min_value=1, value=5)
        df = get_low_stock_products(threshold)
        if not df.empty:
            st.dataframe(df)
        else:
            st.success("Semua stok produk aman!")
    
    elif page == "Produk":
        show_header("Manajemen Produk")
        
        tab1, tab2, tab3 = st.tabs(["Daftar Produk", "Update Stok", "Update Harga"])
        
        with tab1:
            st.subheader("Daftar Produk")
            try:
                conn = get_connection()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM products")
                    product_list = cursor.fetchall()
                    
                    for product in product_list:
                        display_product_card(product)
            except mysql.connector.Error as err:
                st.error(f"Error: {err}")
            finally:
                if conn:
                    conn.close()
        
        with tab2:
            st.subheader("Perbarui Stok Bunga")
            bunga_list = get_bunga_list()
            bunga_names = [bunga['bungaName'] for bunga in bunga_list]
            selected_bunga_name = st.selectbox("Pilih Bunga", bunga_names, key="stok_select")
            selected_bunga = next((b for b in bunga_list if b['bungaName'] == selected_bunga_name), None)
            tambahStock = st.number_input("Jumlah Stock yang Ditambahkan", min_value=1, step=1, key="stok_input")
            if st.button("Tambah Stock", type="primary", key="tambah_stok_btn"):
                if selected_bunga and tambahStock > 0:
                    success = update_stock(selected_bunga['bungaID'], tambahStock)
                    if success:
                        st.session_state.stok_diperbarui = True
                        st.session_state.bunga_terakhir = selected_bunga_name
                        st.session_state.jumlah_tambah = tambahStock
                        st.rerun()
            if st.session_state.get("stok_diperbarui"):
                st.success(f"Stok bunga {st.session_state.bunga_terakhir} berhasil ditambahkan sebanyak {st.session_state.jumlah_tambah} tangkai!")
                st.session_state.stok_diperbarui = False

        with tab3:
            st.subheader("Update Harga Bunga")
            bunga_list = get_bunga_list()
            bunga_names = [bunga['bungaName'] for bunga in bunga_list]
            selected_bunga_name = st.selectbox("Pilih Bunga", bunga_names, key="update_harga_select")
            selected_bunga = next((b for b in bunga_list if b['bungaName'] == selected_bunga_name), None)
            new_price = st.number_input("Harga Baru", min_value=0, key="update_harga_input")
            if st.button("Update Harga", type="primary", key="update_harga_btn"):
                success = update_bunga_price(selected_bunga['bungaID'], new_price)
                if success:
                    st.session_state.harga_diperbarui = True
                    st.rerun()
            if st.session_state.get("harga_diperbarui"):
                st.success(f"Harga bunga {st.session_state.bunga_terakhir} berhasil diperbarui!")
                st.session_state.harga_diperbarui = False

    elif page == "Pelanggan":
        show_header("Manajemen Pelanggan")
        
        tab1, tab2 = st.tabs(["Daftar Pelanggan", "Hapus Pelanggan"])
        
        with tab1:
            st.subheader("Daftar Pelanggan")
            search_query = st.text_input("Cari Pelanggan (Nama/Email)", "")
            customer_id = st.text_input("Cari berdasarkan ID Pelanggan", "")
            data_customers = get_customers(search_query, customer_id)
            st.dataframe(data_customers)
        
        with tab2:
            st.subheader("Hapus Pelanggan")
            custID = st.number_input("ID Pelanggan yang akan dihapus", min_value=1, step=1)
            if st.button("Hapus Pelanggan", type="primary"):
                delete_customer(custID)
    
    elif page == "Pesanan":
        show_header("Manajemen Pesanan")
        
        tab1, tab2, tab3 = st.tabs(["Pesanan Pelanggan", "Daftar Pesanan", "Daftar Detail Pesanan"])
        
        with tab1:
            subtab1, subtab2, subtab3, subtab4 = st.tabs(["Buat Pesanan", "Riwayat Pesanan", "Informasi Pesanan", "Update Status"])

            with subtab1:
                st.subheader("Buat Pesanan Baru")
                custID = st.number_input("Customer ID", min_value=1, step=1, key="customer_new_order")
                paymentMethod = st.selectbox("Metode Pembayaran", ["Cash", "OVO", "Gopay", "Dana"])
                bunga_list = get_bunga_list()
                bunga_names = [bunga['bungaName'] for bunga in bunga_list]
                selected_bunga_name = st.selectbox("Pilih Bunga", bunga_names)
                selected_bunga = next((b for b in bunga_list if b['bungaName'] == selected_bunga_name), None)
                kuantitasTangkai = st.number_input("Jumlah Tangkai", min_value=1, max_value=10, step=1)
                custom = st.selectbox("Warna Custom", ["Pink", "Brown", "Blue", "Green", "Grey", "Yellow", "White", "Purple"])
                if st.button("Buat Pesanan", type="primary", key="new_order_btn"):
                    create_new_order(custID, paymentMethod, selected_bunga['bungaID'], kuantitasTangkai, custom)

            with subtab2:
                st.subheader("Riwayat Pesanan Pelanggan")
                custID = st.number_input("Masukkan Customer ID", min_value=1, step=1, key="customer_orders_history")
                if custID:
                    df = get_customer_orders(custID)
                    if not df.empty:
                        st.dataframe(df)
                    else:
                        st.warning("Pelanggan ini belum pernah memesan.")
            
            with subtab3:
                st.subheader("Informasi Pesanan Pelanggan")
                cust_id = st.number_input("Customer ID", min_value=1, step=1, key="customer_order_details")
                order_id = st.text_input("Masukkan Order ID:", key="customer_details_order_id")
                if st.button("Lihat Detail", type="primary", key="customer_order_details_btn"):
                    if not order_id:
                        st.warning("Mohon masukkan Order ID terlebih dahulu.")
                    else:
                        show_order_details(order_id, cust_id)

            with subtab4:
                st.subheader("Perbarui Status Pesanan Pelanggan")
                orderID = st.number_input("Order ID", min_value=1, step=1, key="update_status_order_id")
                newStatus = st.selectbox("Status Baru", ["Processed", "Shipped", "Completed", "Cancelled"], key="update_status_new_status")                
                if st.button("Perbarui Status", type="primary", key="update_status_btn"):
                    success = update_order_status(orderID, newStatus)
                    if success:
                        st.session_state.status_diperbarui = True
                        st.rerun()
                if st.session_state.get("status_diperbarui"):
                    st.success(f"Status pesanan {orderID} berhasil diperbarui menjadi '{newStatus}'!")
                    st.session_state.status_diperbarui = False

        with tab2:
            st.subheader("Daftar Pesanan")
            search_query = st.text_input("Cari Order ID", "", key="order_search_query")
            status_filter = st.selectbox("Filter Status", ["", "Processed", "Shipped", "Completed", "Cancelled"], key="order_status_filter")
            order_date_filter = st.date_input("Filter Tanggal Pesanan", value=None, key="order_date_filter")
            payment_method_filter = st.selectbox("Filter Metode Pembayaran", ["", "Dana", "OVO", "Gopay", "Cash"], key="order_payment_filter")
            data_orders = get_orders(search_query, status_filter, order_date_filter, payment_method_filter)
            st.dataframe(data_orders, use_container_width=True)

        with tab3:
            st.subheader("Daftar Detail Pesanan")
            search_query = st.text_input("Cari Order Details ID", "", key="details_search_query")
            search_orderID = st.text_input("Cari Order ID", "", key="details_search_order_id")
            bunga_id_filter = st.selectbox("Filter Bunga ID", [""] + [str(i) for i in range(1, 6)], key="details_bunga_id_filter")
            kuantitas_filter = st.selectbox("Filter Jumlah Tangkai", [""] + [str(i) for i in range(1, 11)], key="details_kuantitas_filter")
            custom_filter = st.selectbox(
                "Filter Warna Custom",
                ["", "Green", "Brown", "Blue", "Purple", "Yellow", "Grey", "White", "Pink"],
                key="details_custom_filter"
            )
            data_order_details = get_order_details(search_query, search_orderID, bunga_id_filter, kuantitas_filter, custom_filter)
            st.dataframe(data_order_details, use_container_width=True)

    elif page == "Laporan Penjualan":
        show_header("Laporan Penjualan")
        
        tab1, tab2 = st.tabs(["Produk Terlaris", "Pendapatan"])
        
        with tab1:
            st.subheader("Produk Bunga Terlaris")
            data_produk_terlaris = get_top_selling_products()
            if not data_produk_terlaris.empty:
                fig, ax = plt.subplots()
                ax.bar(data_produk_terlaris["Nama Bunga"], data_produk_terlaris["Total Terjual"], color='#ff6b6b')
                ax.set_xlabel("Nama Bunga")
                ax.set_ylabel("Jumlah Terjual")
                ax.set_title("Produk Bunga Terlaris")
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("Belum ada data penjualan bunga.")
        
        with tab2:
            st.subheader("Pendapatan")
            
            st.subheader("Pendapatan Berdasarkan Rentang Tanggal")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Tanggal Mulai")
            with col2:
                end_date = st.date_input("Tanggal Selesai")
            if st.button("Hitung Pendapatan", type="primary"):
                total_income = get_income_between_dates(start_date, end_date)
                st.success(f"Total Pendapatan: Rp{total_income:,}")
            
            st.subheader("Grafik Pendapatan Bulanan")
            df = get_monthly_revenue()
            if not df.empty:
                fig, ax = plt.subplots()
                ax.plot(df["Bulan"], df["Pendapatan"], marker="o", linestyle="-", color="#ff6b6b")
                ax.set_xlabel("Bulan")
                ax.set_ylabel("Pendapatan (Rp)")
                ax.set_title("Tren Pendapatan Bulanan")
                ax.grid(True)
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("Belum ada data pendapatan.")

# Halaman Customer
elif st.session_state.user_info['role'] == 'customer':
    if page == "Beranda":
        show_header("Beranda")
        st.subheader("Produk Terpopuler")
        display_products_grid()
    
    elif page == "Produk":
        show_header("Katalog Produk")
        
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM products")
                product_list = cursor.fetchall()
                
                for product in product_list:
                    display_product_card(product)
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
        finally:
            if conn:
                conn.close()
    
    elif page == "Pesanan":
        show_header("Pesanan")
        
        tab1, tab2, tab3 = st.tabs(["Riwayat Pesanan", "Informasi Pesanan", "Batalkan Pesanan"])

        username = st.session_state.username
        cust_id = extract_cust_id_from_username(username)
        
        if cust_id:
            with tab1:
                st.subheader("Riwayat Pesanan")
                df = get_customer_orders(cust_id)
                if not df.empty:
                    st.dataframe(df)
                else:
                    st.warning("Anda belum pernah memesan.")
            
            with tab2:
                st.subheader("Informasi Pesanan")
                order_id = st.text_input("Masukkan Order ID:", key="customer_details_order_id")
                if st.button("Lihat Detail", type="primary", key="customer_order_details_btn"):
                    if not order_id:
                        st.warning("Mohon masukkan Order ID terlebih dahulu.")
                    else:
                        show_order_details(order_id, cust_id)

            with tab3:
                st.subheader("Batalkan Pesanan")
                order_id = st.text_input("Masukkan Order ID yang ingin dibatalkan:", key="cancel_order_input")
                if st.button("Batalkan Pesanan", type="primary", key="cancel_order_btn"):
                    if not order_id:
                        st.warning("Mohon masukkan Order ID terlebih dahulu.")
                    else:
                        cancel_order(order_id, cust_id)
                        st.session_state.order_dibatalkan = True
                        st.session_state.last_cancelled_order = order_id
                        st.rerun()
                # Tampilkan status setelah rerun
                if st.session_state.get("order_dibatalkan"):
                    st.success(f"Pesanan {st.session_state.last_cancelled_order} berhasil dibatalkan!")
                    st.session_state.order_dibatalkan = False

    elif page == "Informasi Akun":
        show_header("Informasi Akun")
        
        tab1, tab2 = st.tabs(["Info Akun", "Ganti Password"])
        
        with tab1:
            st.subheader("Informasi Akun")
            
            username = st.session_state.username
            custID = extract_cust_id_from_username(username)
            
            if custID:
                info = get_customer_info(custID)
                if info:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("Nama Depan", value=info['firstName'], disabled=True)
                        st.text_input("Email", value=info['email'], disabled=True)
                        st.text_input("Username", value=info['username'], disabled=True)
                    with col2:
                        st.text_input("Nama Belakang", value=info['lastName'], disabled=True)
                        st.text_input("Nomor Telepon", value=info['phoneNumber'], disabled=True)
                    st.text_area("Alamat", value=info['address'], disabled=True)
                else:
                    st.error("Gagal mengambil data akun.")
            else:
                st.error("Gagal membaca Customer ID.")
        
        with tab2:
            st.subheader("Ganti Password")
            
            username = st.session_state.username
            with st.form(key="change_password_form"):
                old_password = st.text_input("Password Lama", type="password")
                new_password = st.text_input("Password Baru", type="password")
                confirm_password = st.text_input("Konfirmasi Password Baru", type="password")
                
                if st.form_submit_button("Ganti Password", type="primary"):
                    if old_password and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("Password baru dan konfirmasi password tidak cocok!")
                        else:
                            if verify_old_password(username, old_password):
                                if update_password(username, new_password):
                                    st.success("Password berhasil diganti!")
                                else:
                                    st.error("Terjadi kesalahan saat mengupdate password.")
                            else:
                                st.error("Password lama salah!")
                    else:
                        st.error("Semua kolom harus diisi!")
