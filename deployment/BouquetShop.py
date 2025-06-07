import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import io
import psycopg2
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env Supabase credentials
load_dotenv()

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    return create_client(url, key)

supabase = get_supabase_client()

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
    response = supabase.table("products").select("*").execute()
    product_list = response.data

    if not product_list:
        st.warning("Belum ada produk.")
        return

    cols = st.columns(3)
    for idx, product in enumerate(product_list):
        with cols[idx % 3]:
            try:
                st.image(f"images/{product['bungaID']}.jpg", use_container_width=True)
            except:
                st.image("https://via.placeholder.com/200x200.png?text=Bouquet", use_container_width=True)
            st.write(f"**{product['bungaName']}**")
            st.write(f"Rp {product['hargaPerTangkai']:,.2f}")
            st.write(f"Stok: {product['stock']} tangkai")

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
    response = supabase.table("users")\
        .select("*")\
        .eq("username", username)\
        .eq("password", password)\
        .eq("role", "admin")\
        .single()\
        .execute()

    return response.data  # None if tidak ditemukan

def customer_login(username, password):
    response = supabase.table("users")\
        .select("*")\
        .eq("username", username)\
        .eq("password", password)\
        .eq("role", "customer")\
        .single()\
        .execute()

    return response.data  # None jika tidak ditemukan

# Fungsi untuk mengekstrak custID dari username
def extract_cust_id_from_username(username):
    cust_id = None
    if username.lower().startswith('customer'):
        try:
            cust_id = int(username[8:])
        except ValueError:
            return None
    return cust_id

def add_customer(first_name, last_name, email, phone_number, address, password):
    # 1. Insert ke tabel `customers`
    customer_insert = supabase.table("customers").insert({
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "phoneNumber": phone_number,
        "address": address
    }).execute()

    if not customer_insert.data:
        st.error("Gagal membuat customer.")
        return

    # 2. Ambil ID hasil insert (auto dari Supabase)
    customer_id = customer_insert.data[0]["custID"]  # pastikan kolom ini sesuai

    username = f"customer{customer_id}"

    # 3. Insert ke tabel `users`
    user_insert = supabase.table("users").insert({
        "username": username,
        "password": password,
        "role": "customer"
    }).execute()

    if user_insert.data:
        st.success(f"Customer berhasil dibuat! Username Anda: {username}")
    else:
        st.error("Gagal menambahkan ke tabel users.")


# Fungsi untuk membuat pesanan baru
def create_new_order(custID, paymentMethod, bungaID, kuantitasTangkai, custom):
    response = supabase.table("orders").insert({
        "custID": custID,
        "paymentMethod": paymentMethod,
        "status": "Processed",
        "totalPrice": 0  # Calculate if needed
    }).execute()

    if response.data:
        order_id = response.data[0]['orderID']
        supabase.table("orderdetails").insert({
            "orderID": order_id,
            "bungaID": bungaID,
            "kuantitasTangkai": kuantitasTangkai,
            "custom": custom,
            "hargaUnit": 0  # Calculate if needed
        }).execute()
        st.success("Pesanan berhasil dibuat!")
    else:
        st.error("Gagal membuat pesanan.")

# Fungsi untuk memperbarui status pesanan
def update_order_status(orderID, newStatus):
    response = supabase.table("orders").update({"status": newStatus}).eq("orderID", orderID).execute()
    return response.data is not None

# Fungsi untuk memperbarui stok produk
def update_stock(bungaID, tambahStock):
    # Get current stock
    res = supabase.table("products").select("stock").eq("bungaID", bungaID).single().execute()
    if res.data:
        current_stock = res.data["stock"]
        new_stock = current_stock + tambahStock
        update_res = supabase.table("products").update({"stock": new_stock}).eq("bungaID", bungaID).execute()
        if update_res.data:
            st.success(f"Stok bunga berhasil ditambahkan sebanyak {tambahStock} tangkai!")

# Fungsi untuk mengambil data produk terlaris
def get_top_selling_products():
    response = supabase.rpc("top_selling_products").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["Nama Bunga", "Total Terjual"])

# Fungsi untuk mengambil data customer
def get_customers(search_query="", custid=""):
    query = supabase.table("customers").select("*")
    if search_query:
        query = query.ilike("firstName", f"%{search_query}%")
    result = query.execute()
    return pd.DataFrame(result.data) if result.data else pd.DataFrame()

# Fungsi untuk mengambil data orders
def get_orders(search_query="", status="", order_date="", payment_method=""):
    query = supabase.table("orders").select("*")

    if search_query:
        query = query.ilike("orderID", f"%{search_query}%")  # pakai ilike untuk LIKE %...%

    if status:
        query = query.eq("status", status)

    if order_date:
        query = query.eq("orderDate", str(order_date))  # pastikan format date cocok dengan Postgres

    if payment_method:
        query = query.eq("paymentMethod", payment_method)

    response = query.execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["orderID", "custID", "orderDate", "status", "totalPrice", "paymentMethod"])


# Fungsi untuk mengambil data order details
def get_order_details(search_query="", search_orderID="", bungaID="", kuantitasTangkai="", custom=""):
    query = supabase.table("orderdetails").select("*")

    if search_query:
        query = query.eq("orderDetailsID", search_query)

    if search_orderID:
        query = query.eq("orderID", search_orderID)

    if bungaID:
        query = query.eq("bungaID", bungaID)

    if kuantitasTangkai:
        query = query.eq("kuantitasTangkai", kuantitasTangkai)

    if custom:
        query = query.eq("custom", custom)

    response = query.execute()

    return pd.DataFrame(response.data) if response.data else pd.DataFrame(
        columns=["orderDetailsID", "orderID", "bungaID", "kuantitasTangkai", "hargaUnit", "custom"]
    )


# Fungsi untuk mengambil data pendapatan bulanan
def get_monthly_revenue():
    """
    Mengambil data pendapatan bulanan dengan memanggil fungsi PostgreSQL 'get_monthly_revenue' 
    melalui Supabase RPC.
    """
    try:
        # Panggil fungsi 'get_monthly_revenue' yang ada di database menggunakan rpc
        # Tidak perlu menulis query SQL di dalam kode Python lagi
        response = supabase.rpc('get_monthly_revenue').execute()
        
        # Data yang dikembalikan sudah dalam format list of dictionaries
        data = response.data
        
        # Jika tidak ada data, kembalikan DataFrame kosong
        if not data:
            return pd.DataFrame(columns=["Bulan", "Pendapatan"])
        
        # Ubah list of dictionaries menjadi DataFrame
        df = pd.DataFrame(data)
        
        # Ganti nama kolom sesuai keinginan Anda
        df = df.rename(columns={"month": "Bulan", "revenue": "Pendapatan"})
        
        return df

    except Exception as e:
        st.error(f"Gagal mengambil data pendapatan: {e}")
        # Kembalikan DataFrame kosong jika terjadi error
        return pd.DataFrame(columns=["Bulan", "Pendapatan"])

# Fungsi Hapus Customer
def delete_customer(custID):
    """
    Menghapus customer dan user terkait dengan memanggil satu fungsi RPC 
    'delete_customer_and_user' di Supabase.
    """
    try:
        # Panggil fungsi tunggal dengan parameter cust_id
        # Kunci dictionary ('cust_id') harus cocok dengan nama parameter di fungsi SQL
        response = supabase.rpc('delete_customer_and_user', {'cust_id': custID}).execute()
        
        # Tampilkan pesan sukses yang dikembalikan oleh fungsi PostgreSQL
        st.success(response.data)
        
    except Exception as e:
        st.error(f"Terjadi error: {e}")

# Riwayat Pesanan Customer
def get_customer_orders(custID):
    response = supabase.table("orders").select("*").eq("custID", custID).order("orderDate", desc=True).execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

# 5 Pesanan Terakhir
def get_last_five_orders():
    """
    Mengambil 5 pesanan terakhir dan memformatnya persis seperti kode asli.
    """
    try:
        # Menggunakan nama kolom lowercase 'orderdate' untuk menghindari error case-sensitivity
        # yang pernah terjadi sebelumnya. Sesuaikan jika nama kolom Anda berbeda.
        response = supabase.table('orders') \
                           .select('*') \
                           .order('orderDate', desc=True) \
                           .limit(5) \
                           .execute()

        # Jika tidak ada data sama sekali, langsung kembalikan DataFrame kosong
        # dengan kolom yang sudah benar.
        if not response.data:
            return pd.DataFrame(columns=["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"])

        df = pd.DataFrame(response.data)
        
        # Dictionary untuk mengganti nama kolom dari nama database ke nama yang lebih ramah pengguna.
        # Ini jauh lebih aman daripada df.columns = [...] karena tidak bergantung pada urutan.
        # Gunakan nama kolom aktual dari database Anda di sini (kemungkinan besar camelCase atau lowercase).
        column_mapping = {
            'orderID': 'Order ID',
            'custID': 'Customer ID',
            'orderDate': 'Order Date',
            'status': 'Status',
            'totalPrice': 'Total Price',
            'paymentMethod': 'Payment Method'
        }
        
        # Ganti nama kolom yang ada di dalam mapping
        df = df.rename(columns=column_mapping)
        
        # Daftar kolom yang diinginkan dalam urutan yang benar, sesuai kode asli Anda
        desired_columns = ["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"]
        
        # Filter DataFrame untuk memastikan hanya kolom ini yang ada dan dalam urutan ini.
        # Ini akan membuang kolom lain dari `SELECT *` yang mungkin tidak Anda inginkan.
        final_df = df[desired_columns]
        
        return final_df

    except Exception as e:
        st.error(f"Gagal mengambil data pesanan terakhir: {e}")
        # Kembalikan DataFrame kosong dengan kolom yang benar untuk konsistensi
        return pd.DataFrame(columns=["Order ID", "Customer ID", "Order Date", "Status", "Total Price", "Payment Method"])

# Stok Bunga Rendah
def get_low_stock_products(threshold=5):
    """
    Mengambil produk dengan stok rendah sesuai logika kode asli.
    """
    try:
        # Membangun query menggunakan metode Supabase
        response = supabase.table('products') \
                           .select('bunganame, stock') \
                           .lte('stock', threshold) \
                           .order('stock') \
                           .execute()

        # Mengubah hasil menjadi DataFrame dan memberikan nama kolom
        # persis seperti pada kode asli Anda.
        df = pd.DataFrame(response.data, columns=['bunganame', 'stock'])
        df = df.rename(columns={'bunganame': 'Nama Bunga', 'stock': 'Stok'})
        
        return df

    except Exception as e:
        st.error(f"Gagal mengambil data stok produk: {e}")
        # Kembalikan DataFrame kosong jika terjadi error
        return pd.DataFrame(columns=['Nama Bunga', 'Stok'])

# Update Harga Bunga
def update_bunga_price(bungaID, new_price):
    """
    Memperbarui harga bunga di tabel 'products' menggunakan Supabase SDK.
    """
    try:
        # Data yang akan diupdate dimasukkan dalam format dictionary
        response = supabase.table('products') \
                           .update({'hargaPerTangkai': new_price}) \
                           .eq('bungaID', bungaID) \
                           .execute()

        # Operasi update yang berhasil akan mengembalikan data yang telah diperbarui.
        # Jika tidak ada data yang kembali, berarti bungaID tidak ditemukan.
        if response.data:
            st.success(f"Harga untuk Bunga ID {bungaID} berhasil diperbarui.")
            return True
        else:
            st.warning(f"Tidak ada produk yang ditemukan dengan ID {bungaID}. Harga tidak diubah.")
            return False

    except Exception as e:
        st.error(f"Terjadi error saat memperbarui harga: {e}")
        return False

# Pendapatan Berdasarkan Tanggal
def get_income_between_dates(start_date, end_date):
    """
    Menghitung total pendapatan antara dua tanggal dengan memanggil fungsi RPC
    'get_total_income_between' di Supabase.
    """
    try:
        # Panggil fungsi RPC dengan parameter yang dibutuhkan.
        # Nama key di dictionary ('start_date', 'end_date') harus sama
        # dengan nama parameter di fungsi SQL yang Anda buat.
        # Pastikan start_date dan end_date adalah string format 'YYYY-MM-DD'
        response = supabase.rpc(
            'get_total_income_between',
            {'start_date': str(start_date), 'end_date': str(end_date)}
        ).execute()

        # Hasilnya adalah nilai tunggal yang ada di response.data
        total_income = response.data

        # Kembalikan hasilnya, atau 0 jika hasilnya None (tidak ada pendapatan)
        return total_income if total_income is not None else 0

    except Exception as e:
        st.error(f"Gagal menghitung pendapatan: {e}")
        # Kembalikan 0 jika terjadi error
        return 0

# Fungsi ambil data customer dari database
def get_customer_info(custID):
    """
    Mengambil informasi gabungan customer dari tabel customers dan users
    dengan memanggil satu fungsi RPC 'get_customer_details'.
    """
    try:
        # Panggil fungsi RPC dengan parameter yang dibutuhkan
        response = supabase.rpc('get_customer_details', {'p_custid': custID}).execute()

        # response.data akan berisi list. Jika customer ditemukan,
        # list akan berisi satu dictionary. Jika tidak, list akan kosong.
        if response.data:
            return response.data[0]  # Kembalikan dictionary info customer
        else:
            return None  # Customer tidak ditemukan

    except Exception as e:
        st.error(f"Gagal mengambil informasi customer: {e}")
        return None

# Fungsi untuk memverifikasi password lama
def verify_old_password(username, old_password):
    """
    Memverifikasi password lama dengan aman menggunakan fungsi RPC di database.
    """
    try:
        # Panggil fungsi RPC yang aman untuk verifikasi
        response = supabase.rpc(
            'verify_user_password',
            {'p_username': username, 'p_password': old_password}
        ).execute()

        # response.data akan berisi True atau False
        return response.data

    except Exception as e:
        st.error(f"Terjadi error saat verifikasi: {e}")
        return False

# Fungsi untuk mengupdate password baru
def update_password(username, new_password):
    """
    Memperbarui password user dengan aman dengan memanggil fungsi RPC
    yang melakukan hashing di sisi database.
    """
    try:
        # Panggil fungsi RPC yang aman. Password baru dikirim sebagai teks biasa
        # tetapi akan di-hash oleh fungsi di database.
        response = supabase.rpc(
            'update_user_password',
            {'p_username': username, 'p_new_password': new_password}
        ).execute()

        # Fungsi RPC mengembalikan True jika berhasil, atau False jika user tidak ditemukan.
        if response.data:
            st.success("Password berhasil diperbarui.")
            return True
        else:
            st.warning(f"User '{username}' tidak ditemukan. Password tidak diubah.")
            return False

    except Exception as e:
        st.error(f"Terjadi error saat memperbarui password: {e}")
        return False

# Dashboard
def get_summary():
    """
    Mengambil data ringkasan dengan panggilan Supabase SDK langsung, tanpa RPC.
    """
    try:
        # 1. Menghitung total customers menggunakan fitur `count` di SDK
        total_customers = supabase.table('customers').select(
            '*', count='exact'
        ).execute().count

        # 2. Menghitung total orders dengan cara yang sama
        total_orders = supabase.table('orders').select(
            '*', count='exact'
        ).execute().count

        # 3. Mengambil SEMUA harga dari tabel orders dan menjumlahkannya di Python
        # Ini adalah cara untuk melakukan SUM tanpa RPC.
        income_response = supabase.table('orders').select('totalPrice').execute()
        
        # Jumlahkan secara manual jika ada datanya
        if income_response.data:
            # Pastikan hanya menjumlahkan angka dan mengabaikan nilai None (kosong)
            total_income = sum(
                item['totalPrice'] for item in income_response.data if item.get('totalPrice') is not None
            )
        else:
            total_income = 0

        return total_customers, total_orders, total_income

    except Exception as e:
        st.error(f"Gagal mengambil data ringkasan: {e}")
        return 0, 0, 0

# Fungsi untuk mendapatkan nama bunga
def get_bunga_list():
    """
    Mengambil daftar ID dan nama bunga dari tabel 'products'
    menggunakan Supabase SDK.
    """
    try:
        # Pilih kolom 'bungaID' dan 'bungaName' dari tabel 'products'
        response = supabase.table('products') \
                           .select('bungaID, bungaName') \
                           .execute()

        # response.data secara otomatis adalah list of dictionaries,
        # sesuai dengan format yang Anda inginkan.
        return response.data

    except Exception as e:
        st.error(f"Gagal mengambil daftar bunga: {e}")
        # Kembalikan list kosong jika terjadi error
        return []

# Detail Pesanan
def show_order_details(order_id, customer_id):
    """
    Menampilkan detail pesanan lengkap menggunakan fitur JOIN native dari Supabase.
    Memerlukan setup Foreign Key di database.
    """
    try:
        # Query ini mengambil data dari 'orders' dan secara otomatis menyertakan
        # data terkait dari 'orderdetails', dan di dalamnya juga data dari 'products'.
        response = supabase.table('orders') \
                           .select('*, orderdetails(*, products(*))') \
                           .eq('orderID', order_id) \
                           .eq('custID', customer_id) \
                           .execute()

        details = response.data

        if not details:
            st.error("Pesanan tidak ditemukan atau bukan milik Customer ini.")
        else:
            order_info = details[0] # Karena hanya ada satu pesanan yang cocok
            
            st.subheader(f"Detail Pesanan (Order ID: {order_id})")
            st.write(f"**Tanggal Pesanan:** {order_info['orderDate']}")
            st.write(f"**Metode Pembayaran:** {order_info['paymentMethod']}")
            st.write(f"**Status:** {order_info['status']}")
            st.write(f"**Total Harga Pesanan:** Rp {order_info['totalPrice']:,}")
            st.markdown("---")
            
            st.write("**Daftar Item Pesanan:**")
            # Loop melalui list 'orderdetails' yang ada di dalam data pesanan
            for item in order_info['orderdetails']:
                # Akses info produk yang bersarang di dalam setiap item
                product_info = item.get('products', {})
                st.write(f"- **Nama Bunga:** {product_info.get('bungaName', 'N/A')}")
                st.write(f"  - Jumlah Tangkai: {item['kuantitasTangkai']}")
                st.write(f"  - Custom: {item['custom']}")
                st.markdown("---")

    except Exception as e:
        st.error(f"Terjadi error saat mengambil detail pesanan: {e}")


# Batalkan Pesanan

def cancel_order(order_id, customer_id):
    """
    Membatalkan pesanan dengan aman menggunakan satu panggilan RPC
    yang berisi semua logika bisnis.
    """
    try:
        # Panggil fungsi tunggal yang melakukan semua validasi dan update
        response = supabase.rpc(
            'cancel_customer_order',
            {'p_order_id': order_id, 'p_customer_id': customer_id}
        ).execute()

        result_message = response.data

        # Interpretasikan pesan yang dikembalikan oleh fungsi database
        if result_message == 'Success':
            st.success(f"Pesanan {order_id} berhasil dibatalkan.")
        elif result_message == 'Not Found':
            st.error("Pesanan tidak ditemukan atau bukan milik Anda.")
        elif result_message and result_message.startswith('Cannot Cancel'):
            # Ambil status dari pesan, contoh: 'Cannot Cancel: Shipped' -> 'Shipped'
            status = result_message.split(': ')[1]
            st.warning(f"Pesanan tidak bisa dibatalkan karena statusnya sudah '{status}'.")
        else:
            st.error("Terjadi kesalahan yang tidak diketahui.")
            
    except Exception as e:
        st.error(f"Error saat mencoba membatalkan pesanan: {e}")

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
                
                with supabase.cursor() as cursor:
                    cursor.execute("SELECT * FROM products")
                    product_list = cursor.fetchall()
                    
                    for product in product_list:
                        display_product_card(product)
            except mysql.connector.Error as err:
                st.error(f"Error: {err}")
            finally:
                if supabase:
                    supabase.close()
        
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
            
            with supabase.cursor() as cursor:
                cursor.execute("SELECT * FROM products")
                product_list = cursor.fetchall()
                
                for product in product_list:
                    display_product_card(product)
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
        finally:
            if supabase:
                supabase.close()
    
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