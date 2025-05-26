# ui_components.py
import streamlit as st

# Semua CSS Anda dari BouquetShop.py masuk ke sini
APP_STYLES = """
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
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        cursor: pointer;
    }
    .btn-primary:hover {
        background-color: #ff5252;
    }
    input[type="text"], input[type="number"] {
        color: white !important;
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
        padding: 6.25px !important;
        border-top: 1px solid #ddd !important;
    }
    .stSelectbox > div > div {
        color: white !important;
        border: 1px solid #ddd !important;
        border-radius: 6px !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        color: white !important;
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
        color: white !important;
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
    .metric-card div[style*="font-size:2em"] { /* Penyesuaian untuk ikon */
        font-size: 20px !important; /* Ukuran ikon yang lebih kecil */
        margin-bottom: 5px !important;
    }
</style>
"""

def apply_styles():
    st.markdown(APP_STYLES, unsafe_allow_html=True)

def show_header(title):
    st.markdown(f"""
        <div class="header">
            <h1 style="margin:0; display:flex; align-items:center;">
                <span style="margin-right:10px;">💐</span>
                {title}
            </h1>
        </div>
    """, unsafe_allow_html=True)

def display_product_card(product_data, current_role, extract_id_func, create_order_func):
    # product_data adalah dictionary dari get_all_products()
    # {'bungaID': ..., 'bungaName': ..., 'hargaPerTangkai': ..., 'stock': ...}
    
    # Pastikan product_data tidak None dan memiliki kunci yang diharapkan
    if not product_data or not all(k in product_data for k in ['bungaID', 'bungaName', 'hargaPerTangkai', 'stock']):
        st.warning("Data produk tidak lengkap.")
        return

    product_id = product_data['bungaID']
    product_name = product_data['bungaName']
    product_price = product_data['hargaPerTangkai']
    product_stock = product_data['stock']

    # Wrapper div untuk styling card produk individual
    st.markdown(f"""
    <div class="product-card">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        try:
            # Asumsikan path gambar relatif terhadap folder tempat app.py dijalankan
            st.image(f"images/{product_id}.jpg", width=150)
        except FileNotFoundError: # Lebih spesifik
            st.image("https://via.placeholder.com/150x150.png?text=Bouquet", width=150)

    with col2:
        st.subheader(product_name)
        st.markdown(f"**Harga:** Rp {product_price:,.2f} per tangkai")
        st.markdown(f"**Stok tersedia:** {product_stock} tangkai")
        st.markdown(f"**ID Produk:** {product_id}")
        
        if current_role == "customer":
            with st.expander("Buat Pesanan"):
                # Key form harus unik untuk setiap produk
                with st.form(key=f"order_form_{product_id}"):
                    paymentMethod = st.selectbox("Metode Pembayaran", ["Cash", "OVO", "Gopay", "Dana"], key=f"pay_{product_id}")
                    # Stok produk sebagai max_value
                    kuantitasTangkai = st.number_input("Jumlah Tangkai", min_value=1, max_value=int(product_stock) if product_stock else 1, step=1, key=f"qty_{product_id}")
                    custom = st.selectbox("Warna Custom", ["Pink", "Brown", "Blue", "Green", "Grey", "Yellow", "White", "Purple"], key=f"custom_{product_id}")
                    
                    if st.form_submit_button("Pesan Sekarang"):
                        username = st.session_state.get("username") # Ambil username dari session_state
                        if username:
                            custID = extract_id_func(username)
                            if custID:
                                if product_stock >= kuantitasTangkai :
                                    result = create_order_func(custID, paymentMethod, product_id, kuantitasTangkai, custom)
                                    if result["success"]:
                                        st.success(result["message"])
                                        # Pertimbangkan untuk memuat ulang data produk atau halaman jika perlu update stok
                                        st.rerun()
                                    else:
                                        st.error(f"Gagal membuat pesanan: {result['message']}")
                                else:
                                    st.error(f"Stok tidak mencukupi. Stok tersedia: {product_stock}")

                            else:
                                st.error("Gagal membuat pesanan. User ID tidak valid.")
                        else:
                             st.error("Sesi pengguna tidak ditemukan. Silakan login kembali.")
    
    st.markdown("</div>", unsafe_allow_html=True) # Penutup div product-card


def display_products_grid(products_list, current_role, extract_id_func, create_order_func):
    # products_list adalah list of dictionaries dari get_all_products()
    if not products_list:
        st.info("Tidak ada produk yang ditampilkan.")
        return

    cols_count = 3 # Jumlah kolom yang diinginkan
    cols = st.columns(cols_count)
    for idx, product_data in enumerate(products_list):
        with cols[idx % cols_count]:
            # Ini adalah versi ringkas untuk grid, jika ingin card penuh panggil display_product_card
            try:
                st.image(f"images/{product_data['bungaID']}.jpg", use_container_width=True, caption=product_data['bungaName'])
            except FileNotFoundError:
                st.image("https://via.placeholder.com/200x200.png?text=Bouquet", use_container_width=True, caption=product_data['bungaName'])
            st.write(f"**{product_data['bungaName']}**")
            st.write(f"Rp {product_data['hargaPerTangkai']:, .2f}")
            st.write(f"Stok: {product_data['stock']} tangkai")
            # Jika ingin tombol pesan langsung di grid, tambahkan expander dan form di sini juga,
            # mirip dengan display_product_card, atau buat tombol "Lihat Detail" yang mengarah ke halaman produk.


def display_metric_card(title, value, icon="投"): # Icon default disesuaikan
    st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:2em; margin-bottom:10px;">{icon}</div>
            <h3>{title}</h3>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)

def show_order_details_component(order_details_list):
    # order_details_list adalah list of dictionaries dari get_full_order_details_for_customer
    if not order_details_list:
        st.error("Detail pesanan tidak ditemukan atau bukan milik Customer.")
        return

    # Ambil informasi umum dari item pertama (karena sama untuk semua item dalam satu pesanan)
    first_item = order_details_list[0]
    st.subheader(f"Detail Pesanan (Order ID: {first_item['orderID']})")
    st.write(f"**Tanggal Pesanan:** {first_item['orderDate']}")
    st.write(f"**Metode Pembayaran:** {first_item['paymentMethod']}")
    st.write(f"**Status:** {first_item['status']}")
    st.write(f"**Total Pesanan:** Rp {first_item['totalPrice']:,.2f}") # Total harga dari tabel orders

    st.markdown("---")
    st.write("**Daftar Item Pesanan:**")

    for item in order_details_list:
        st.markdown(f"""
        - **Nama Bunga:** {item['bungaName']}
          - Jumlah Tangkai: {item['kuantitasTangkai']}
          - Custom: {item['custom']}
        """) # Harga per item tidak ada di query ini, hanya total pesanan.
    st.markdown("---")
