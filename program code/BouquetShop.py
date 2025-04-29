import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Fungsi untuk mendapatkan koneksi database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bouquetshop"
    )

st.title("Bouquet Shop")

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
                    "id": result[0],           # id dari tabel users
                    "username": result[1],     # username dari tabel users
                    "password": result[2],     # password dari tabel users
                    "role": result[3]           # role dari tabel users
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
    # Jika username diawali dengan 'customer', ambil angka setelahnya
    if username.lower().startswith('customer'):
        try:
            # Ambil angka setelah 'customer'
            cust_id = int(username[8:])
        except ValueError:
            return None  # Jika username tidak valid (misalnya bukan angka setelah 'customer')
    return cust_id

# Fungsi untuk menambah customer
def add_customer(first_name, last_name, email, phone_number, address, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insert ke table customer lewat prosedur
        cursor.callproc("AddCustomer", (first_name, last_name, email, phone_number, address))
        conn.commit()

        # Ambil customer_id terakhir
        cursor.execute("SELECT MAX(custID) as customer_id FROM customers")
        result = cursor.fetchone()
        customer_id = result[0]

        # Buat username customer[id]
        username = f"customer{customer_id}"

        # Insert ke table users
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

# Fungsi untuk membuat pesanan baru
def create_new_order(custID, paymentMethod, bungaID, kuantitasTangkai, custom):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("CreateNewOrder", (custID, paymentMethod, bungaID, kuantitasTangkai, custom))
            conn.commit()

        # Ambil last_orderID dari tabel ordersequence
            cursor.execute("SELECT last_orderID FROM ordersequence LIMIT 1;")
            order_id = cursor.fetchone()[0]
            st.success(f"Pesanan berhasil dibuat dengan orderID: {order_id}!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        conn.close()

# Fungsi untuk memperbarui status pesanan
def update_order_status(orderID, newStatus):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("UpdateOrderStatus", (orderID, newStatus))
            conn.commit()
            st.success(f"Status pesanan {orderID} berhasil diperbarui menjadi '{newStatus}'!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        conn.close()

# Fungsi untuk memperbarui stok produk
def update_stock(bungaID, tambahStock):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("UpdateProductStock", (bungaID, tambahStock))
            conn.commit()
            st.success(f"Stok bunga berhasil ditambahkan sebanyak {tambahStock} tangkai!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
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
            return pd.DataFrame(result, columns=["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"])
    finally:
        conn.close()

# Fungsi untuk mengambil data order details
def get_order_details(search_query="", search_orderID="", bungaID="", kuantitasTangkai="", custom=""):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM orderdetails WHERE 1=1"
            params = []

            # Filter berdasarkan orderDetailsID
            if search_query:
                query += " AND orderDetailsID = %s"
                params.append(search_query)  # Tidak pakai LIKE, karena ID biasanya integer

            # Filter berdasarkan orderID
            if search_orderID:
                query += " AND orderID = %s"
                params.append(search_orderID)

            #cursor.execute(query, (f"%{search_query}%",))
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
            # Hapus dari tabel Customers
            cursor.callproc("DeleteCustomer", (custID,))
            conn.commit()

            # Hapus dari tabel Users (username = customer[custID])
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
            st.success("Harga bunga berhasil diperbarui!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
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
            # Ambil dari tabel customers
            query_cust = "SELECT firstName, lastName, email, phoneNumber, address FROM customers WHERE custID = %s"
            cursor.execute(query_cust, (custID,))
            customer_info = cursor.fetchone()
            
            # Ambil username dan password dari tabel users
            username = f"customer{custID}"  # Asumsi username formatnya 'customer{custID}'
            query_user = "SELECT username, password FROM users WHERE username = %s"
            cursor.execute(query_user, (username,))
            user_info = cursor.fetchone()
            
            # Gabungkan kedua info
            if customer_info and user_info:
                return {**customer_info, **user_info}  # Merge dictionaries
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
            result = cursor.fetchone()  # Ambil satu hasil
            if result and result[0] == old_password:  # result[0] adalah password
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

# Inisialisasi session_state
if "role" not in st.session_state:
    st.session_state.role = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

if st.session_state.role is None:
    st.subheader("Selamat Datang di Bouquet Shop!")
    
    pilihan_awal = st.radio("Silakan pilih", ("Login", "Sign Up"))

    if pilihan_awal == "Login":
        role = st.radio("Login sebagai", ("Admin", "Customer"))

        if role == "Admin":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login Admin"):
                user = admin_login(username, password)
                if user:
                    st.success(f"Selamat datang, Admin!")
                    st.session_state.role = "admin"
                    st.session_state.user_info = user
                    st.rerun()
                else:
                    st.error("Username atau password salah!")

        elif role == "Customer":
            username = st.text_input("Username (Format: customerID)")
            password = st.text_input("Password", type="password")
            if st.button("Login Customer"):
                user = customer_login(username, password)
                if user:
                    st.success(f"Selamat datang, Customer!") 
                    st.session_state.role = "customer"
                    st.session_state.user_info = user
                    st.session_state.username = username  # Simpan username ke session state
                    st.rerun()
                else:
                    st.error("Username atau password salah!")

    elif pilihan_awal == "Sign Up":
        st.subheader("Sign Up")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        phone_number = st.text_input("Phone Number")
        address = st.text_area("Address")
        password = st.text_input("Password", type="password")
        
        if st.button("Daftar Customer"):
            add_customer(first_name, last_name, email, phone_number, address, password)

    st.stop()

st.sidebar.title("Navigasi")

if st.session_state.role == 'admin':
    page = st.sidebar.radio("Pilih Menu", [
        "Dashboard", "Pendapatan Berdasarkan Tanggal", "Data Produk", "Data Customers", "Data Orders", "Data Order Details",
        "Hapus Customer", "Buat Pesanan", "Riwayat Pesanan Customer", "Lihat Detail Pesanan",
        "5 Pesanan Terakhir", "Perbarui Status Pesanan", "Laporan Stok Bunga", "Perbarui Stok Bunga",
        "Update Harga Bunga"
    ])
elif st.session_state.user_info['role'] == 'customer':
    page = st.sidebar.radio("Pilih Menu", [
        "Data Produk", "Buat Pesanan", "Riwayat Pesanan Customer", "Lihat Detail Pesanan", "Batalkan Pesanan", "Info Akun", "Ganti Password"
    ])
else:
    page = None

# Dashboard
if page == "Dashboard":
    st.title("Dashboard")
    customers, orders, income = get_summary()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pelanggan", customers)
    col2.metric("Total Pesanan", orders)
    col3.metric("Total Pendapatan", f"Rp{int(income):,}")

    # Ambil data pendapatan
    df = get_monthly_revenue()

    # Jika data tidak kosong, buat grafik
    if not df.empty:
        fig, ax = plt.subplots()
        ax.plot(df["Bulan"], df["Pendapatan"], marker="o", linestyle="-", color="b")
        
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Pendapatan (Rp)")
        ax.set_title("Tren Pendapatan Bulanan")
        ax.grid(True)
        plt.xticks(rotation=45)

        # Tampilkan grafik di Streamlit
        st.pyplot(fig)
    else:
        st.warning("⚠️ Data pendapatan belum tersedia!")

    # Grafik bunga terlaris
    data_produk_terlaris = get_top_selling_products()
    if not data_produk_terlaris.empty:
        fig, ax = plt.subplots()
        ax.bar(data_produk_terlaris["Nama Bunga"], data_produk_terlaris["Total Terjual"], color='pink')
        ax.set_xlabel("Nama Bunga")
        ax.set_ylabel("Jumlah Terjual")
        ax.set_title("Produk Bunga Terlaris")
        st.pyplot(fig)
    else:
        st.warning("Belum ada data penjualan bunga.")

# Halaman Hapus Customer
elif page == "Hapus Customer":
    st.subheader("Hapus Customer")
    custID = st.number_input("Customer ID yang akan dihapus", min_value=1, step=1)
    if st.button("Hapus Customer"):
        delete_customer(custID)

# Halaman Buat Pesanan
elif page == "Buat Pesanan":
    st.subheader("Buat Pesanan")
    if st.session_state.role == "admin":
        custID = st.number_input("Customer ID", min_value=1, step=1)
    else:  # Jika customer
        username = st.session_state.username  # Mengambil username yang sudah disimpan
        custID = extract_cust_id_from_username(username)  # Mengambil custID dari username
    
    paymentMethod = st.selectbox("Metode Pembayaran", ["Cash", "OVO", "Gopay", "Dana"])
    bunga_list = get_bunga_list()
    bunga_names = [bunga['bungaName'] for bunga in bunga_list]
    selected_bunga_name = st.selectbox("Pilih Bunga", bunga_names)
    # Cari bungaID yang sesuai dengan nama bunga yang dipilih
    selected_bunga = next((b for b in bunga_list if b['bungaName'] == selected_bunga_name), None)
    kuantitasTangkai = st.number_input("Jumlah Tangkai", min_value=1, max_value=10, step=1)
    custom = st.selectbox("Custom", ["Pink", "Brown", "Blue", "Green", "Grey", "Yellow", "White", "Purple"])
    if st.button("Buat Pesanan"):
        create_new_order(custID, paymentMethod, selected_bunga['bungaID'], kuantitasTangkai, custom)

# Halaman Riwayat Pesanan Customer
elif page == "Riwayat Pesanan Customer":
    if st.session_state.role == "admin":
        custID = st.number_input("Customer ID", min_value=1, step=1)
    else:  # Jika customer
        username = st.session_state.username  # Mengambil username yang sudah disimpan
        custID = extract_cust_id_from_username(username)  # Mengambil custID dari username

    if custID:
        df = get_customer_orders(custID)
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("Customer ini belum pernah memesan.")

# Halaman 5 Pesanan Terakhir
elif page == "5 Pesanan Terakhir":
    st.subheader("5 Pesanan Terbaru")
    df = get_last_five_orders()
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("Belum ada pesanan.")

# Halaman Perbarui Status Pesanan
elif page == "Perbarui Status Pesanan":
    st.subheader("Perbarui Status Pesanan")
    orderID = st.number_input("Order ID", min_value=1, step=1)
    newStatus = st.selectbox("Pilih Status Baru", ["Processed", "Shipped", "Completed", "Cancelled"])
    if st.button("Perbarui Status"):
        update_order_status(orderID, newStatus)

# Halaman Laporan Stok Bunga
elif page == "Laporan Stok Bunga":
    st.subheader("Laporan Bunga dengan Stok Rendah")
    threshold = st.number_input("Batas Stok Minimum", min_value=1, value=5)
    df = get_low_stock_products(threshold)
    if not df.empty:
        st.dataframe(df)
    else:
        st.success("Semua stok bunga aman!")

# Halaman Perbarui Stok Bunga
elif page == "Perbarui Stok Bunga":
    st.subheader("Perbarui Stok Bunga")

    bunga_list = get_bunga_list()
    bunga_names = [bunga['bungaName'] for bunga in bunga_list]
    
    selected_bunga_name = st.selectbox("Pilih Bunga", bunga_names)

    # Cari bungaID yang sesuai dengan nama bunga yang dipilih
    selected_bunga = next((b for b in bunga_list if b['bungaName'] == selected_bunga_name), None)

    if selected_bunga:
        tambahStock = st.number_input("Jumlah Stok yang Ditambahkan", min_value=1, step=1)
        if st.button("Tambah Stok"):
            update_stock(selected_bunga['bungaID'], tambahStock)


# Halaman Update Harga Bunga
elif page == "Update Harga Bunga":
    st.subheader("Update Harga Bunga")

    bunga_list = get_bunga_list()
    bunga_names = [bunga['bungaName'] for bunga in bunga_list]
    
    selected_bunga_name = st.selectbox("Pilih Bunga", bunga_names)

    # Cari bungaID yang sesuai dengan nama bunga yang dipilih
    selected_bunga = next((b for b in bunga_list if b['bungaName'] == selected_bunga_name), None)
    
    new_price = st.number_input("Harga Baru", min_value=0)
    if st.button("Update Harga"):
        update_bunga_price(selected_bunga['bungaID'], new_price)

# Halaman Pendapatan Berdasarkan Tanggal
elif page == "Pendapatan Berdasarkan Tanggal":
    st.subheader("Pendapatan Berdasarkan Rentang Tanggal")
    start_date = st.date_input("Tanggal Mulai")
    end_date = st.date_input("Tanggal Selesai")
    if st.button("Hitung Pendapatan"):
        total_income = get_income_between_dates(start_date, end_date)
        st.success(f"Total Pendapatan: Rp{total_income:,}")

# Halaman Data Customers
elif page == "Data Customers":
    st.subheader("📋 Data Customers")
    search_query = st.text_input("Cari Customer (Nama/Email)", "")
    customer_id = st.text_input("Cari berdasarkan Customer ID", "")
    data_customers = get_customers(search_query, customer_id)
    st.dataframe(data_customers)

# Halaman Data Orders
elif page == "Data Orders":
    st.subheader("📋 Data Orders")
    search_query = st.text_input("Cari Order ID", "")
    status_filter = st.selectbox("Filter Status", ["", "Processed", "Shipped", "Completed"])
    order_date_filter = st.date_input("Filter Order Date", value=None)
    payment_method_filter = st.selectbox("Filter Metode Pembayaran", ["", "Dana", "OVO", "Gopay", "Cash"])
    data_orders = get_orders(search_query, status_filter, order_date_filter, payment_method_filter)
    st.dataframe(data_orders)

# Halaman Data Order Details
elif page == "Data Order Details":
    st.subheader("📋 Data Order Details")
    search_query = st.text_input("Cari Order Details ID", "")
    search_orderID = st.text_input("Cari Order ID", "")
    bunga_id_filter = st.selectbox("Filter Bunga ID", [""] + [str(i) for i in range(1, 6)])
    kuantitas_filter = st.selectbox("Filter Kuantitas Tangkai", [""] + [str(i) for i in range(1, 11)])
    custom_filter = st.selectbox("Filter Custom", ["", "Green", "Brown", "Blue", "Purple", "Yellow", "Grey", "White", "Pink"])
    data_order_details = get_order_details(search_query, search_orderID, bunga_id_filter, kuantitas_filter, custom_filter)
    st.dataframe(data_order_details)

elif page == "Data Produk":
    st.subheader("Daftar Produk")

    try:
        conn = get_connection()  # Panggil fungsi untuk mendapatkan koneksi
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products")  # Ambil data dari MySQL
            product_list = cursor.fetchall()

            for product in product_list:
                st.write(f"🛒 **{product[1]}** - Rp {product[2]:,.2f} ({product[3]} stok)")

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")

    finally:
        if conn:
            conn.close()  # Pastikan koneksi ditutup setelah digunakan

# Halaman Info Akun
elif page == "Info Akun":
    st.subheader("Informasi Akun Anda")

    # Pastikan user sudah login
    if st.session_state.role == "customer":
        # Dapatkan custID dari username
        username = st.session_state.username
        custID = None
        if username.lower().startswith('customer'):
            try:
                custID = int(username[8:])
            except ValueError:
                st.error("Username tidak valid.")
        
        if custID:
            info = get_customer_info(custID)
            if info:
                st.text_input("First Name", value=info['firstName'], disabled=True)
                st.text_input("Last Name", value=info['lastName'], disabled=True)
                st.text_input("Email", value=info['email'], disabled=True)
                st.text_input("Phone Number", value=info['phoneNumber'], disabled=True)
                st.text_area("Address", value=info['address'], disabled=True)
                st.text_input("Username", value=info['username'], disabled=True)
                st.text_input("Password", value=info['password'], disabled=True)  # Untuk demo, biasanya password tidak ditampilkan
            else:
                st.error("Gagal mengambil data akun.")
        else:
            st.error("Gagal membaca Customer ID.")
    else:
        st.warning("Hanya customer yang bisa melihat halaman ini.")

# Halaman Lihat Detail Pesanan
elif page == "Lihat Detail Pesanan":
    st.title("Lihat Detail Pesanan")

    if st.session_state.role == "admin":
        cust_id = st.number_input("Customer ID", min_value=1, step=1)
    else:  # Jika customer
        username = st.session_state.username  # Mengambil username yang sudah disimpan
        cust_id = extract_cust_id_from_username(username)  # Mengambil custID dari username
    
    order_id = st.text_input("Masukkan Order ID:")

    if st.button("Lihat Detail"):
        if not order_id:
            st.warning("Mohon masukkan Order ID terlebih dahulu.")
        else:
            show_order_details(order_id, cust_id)

# Halaman Batalkan Pesanan
elif page == "Batalkan Pesanan":
    st.title("Batalkan Pesanan")

    username = st.session_state.username  # Mengambil username yang sudah disimpan
    cust_id = extract_cust_id_from_username(username)  # Mengambil custID dari username
    order_id = st.text_input("Masukkan Order ID yang ingin dibatalkan:")

    if st.button("Batalkan Pesanan"):
        if not order_id:
            st.warning("Mohon masukkan Order ID terlebih dahulu.")
        else:
            cancel_order(order_id, cust_id)

# Halaman Ganti Password
elif page == "Ganti Password":
    st.subheader("Ganti Password")

    if st.session_state.role == "customer":
        username = st.session_state.username
        # Input password lama dan password baru
        old_password = st.text_input("Password Lama", type="password")
        new_password = st.text_input("Password Baru", type="password")
        confirm_password = st.text_input("Konfirmasi Password Baru", type="password")

        if st.button("Ganti Password"):
            if old_password and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("Password baru dan konfirmasi password tidak cocok!")
                else:
                    # Verifikasi password lama
                    if verify_old_password(username, old_password):
                        # Update password baru
                        if update_password(username, new_password):
                            st.success("Password berhasil diganti!")
                        else:
                            st.error("Terjadi kesalahan saat mengupdate password.")
                    else:
                        st.error("Password lama salah!")
            else:
                st.error("Semua kolom harus diisi.")
    else:
        st.warning("Hanya customer yang dapat mengganti password.")

if st.sidebar.button("Logout"):
    st.session_state.role = None
    st.session_state.user_info = None
    st.rerun()

