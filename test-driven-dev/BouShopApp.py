# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt # Jika masih digunakan untuk plot
# from PIL import Image # Jika masih digunakan
# import io # Jika masih digunakan

# Impor modul-modul yang sudah dibuat
from db_connection import get_connection # Pastikan ini dari db_connection.py (MySQL)
import auth
import customer_management as cm
import product_management as pm
import order_management as om
import reporting
import ui_components

# Terapkan CSS
ui_components.apply_styles()

# --- Inisialisasi Session State ---
if "role" not in st.session_state:
    st.session_state.role = None
if "user_info" not in st.session_state: # Berisi dict informasi user setelah login
    st.session_state.user_info = None
if "username" not in st.session_state: # Menyimpan username setelah login customer
    st.session_state.username = None
# Tambahkan session state lain yang mungkin diperlukan untuk UI (misal, pesan sementara)
if "temp_message" not in st.session_state: # Untuk pesan sukses/error sementara
    st.session_state.temp_message = None


# --- Tampilkan Pesan Sementara (jika ada) ---
if st.session_state.temp_message:
    msg_type = st.session_state.temp_message["type"]
    msg_text = st.session_state.temp_message["text"]
    if msg_type == "success":
        st.success(msg_text)
    elif msg_type == "error":
        st.error(msg_text)
    elif msg_type == "warning":
        st.warning(msg_text)
    st.session_state.temp_message = None # Hapus setelah ditampilkan


# --- Halaman Login/Signup (Jika belum login) ---
if st.session_state.role is None:
    ui_components.show_header("Bouquet Shop") # Panggil header dari ui_components
    
    pilihan_awal = st.radio("Silakan pilih:", ("Login", "Sign Up"), horizontal=True, key="login_signup_radio")
    
    if pilihan_awal == "Login":
        role_pilihan = st.radio("Login sebagai:", ("Admin", "Customer"), horizontal=True, key="role_login_radio")
        
        if role_pilihan == "Admin":
            with st.form(key="admin_login_form"):
                st.subheader("Login Admin")
                username_input = st.text_input("Username")
                password_input = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login"):
                    user_data = auth.admin_login(username_input, password_input)
                    if user_data:
                        st.session_state.role = "admin"
                        st.session_state.user_info = user_data
                        st.session_state.username = user_data['username'] # Simpan username juga
                        st.session_state.temp_message = {"type": "success", "text": f"Selamat datang, Admin {user_data['username']}!"}
                        st.rerun()
                    else:
                        st.error("Username atau password admin salah!")

        elif role_pilihan == "Customer":
            with st.form(key="customer_login_form"):
                st.subheader("Login Customer")
                username_input = st.text_input("Username (Format: customerID)")
                password_input = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login"):
                    user_data = auth.customer_login(username_input, password_input)
                    if user_data:
                        st.session_state.role = "customer"
                        st.session_state.user_info = user_data
                        st.session_state.username = user_data['username'] # Simpan username dari hasil login
                        st.session_state.temp_message = {"type": "success", "text": f"Selamat datang, Customer!"}
                        st.rerun()
                    else:
                        st.error("Username atau password customer salah!")

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
            new_password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Daftar Sekarang"):
                if all([first_name, last_name, email, phone_number, address, new_password]):
                    result = cm.add_customer(first_name, last_name, email, phone_number, address, new_password)
                    if result["success"]:
                        st.session_state.temp_message = {"type": "success", "text": result["message"]}
                        # Mungkin arahkan ke login atau tampilkan pesan sukses
                    else:
                        st.session_state.temp_message = {"type": "error", "text": f"Gagal mendaftar: {result['message']}"}
                    st.rerun() # Untuk menampilkan pesan
                else:
                    st.error("Semua kolom harus diisi!")
    st.stop() # Hentikan eksekusi jika belum login

# --- Sidebar Navigasi (Setelah Login) ---
st.sidebar.title("💐 Bouquet Shop") # Icon Bunga
user_display_name = st.session_state.user_info.get('username', 'Pengguna') if st.session_state.user_info else 'Pengguna'

if st.session_state.role == 'admin':
    st.sidebar.markdown(f"**Halo, Admin!**")
    page = st.sidebar.radio("Menu Admin", [
        "Beranda", "Produk", "Pelanggan", "Pesanan", "Laporan Penjualan"
    ], key="admin_menu")
elif st.session_state.role == 'customer': # Perbaiki kondisi untuk customer
    st.sidebar.markdown(f"**Halo, Customer!**") # Lebih personal untuk customer
    page = st.sidebar.radio("Menu Customer", [
        "Produk", "Pesanan Saya", "Informasi Akun"
    ], key="customer_menu")

if st.sidebar.button("🚪 Logout"): # Icon Logout
    # Reset semua session state yang relevan
    st.session_state.role = None
    st.session_state.user_info = None
    st.session_state.username = None
    st.session_state.temp_message = {"type": "success", "text": "Anda berhasil logout."}
    st.rerun()


# --- Konten Halaman (Setelah Login) ---

# == HALAMAN ADMIN ==
if st.session_state.role == 'admin':
    if page == "Beranda":
        ui_components.show_header("Beranda Admin")
        total_cust, total_ord, total_inc = reporting.get_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            ui_components.display_metric_card("Total Pelanggan", total_cust, "👥") # Icon Pelanggan
        with col2:
            ui_components.display_metric_card("Total Pesanan", total_ord, "📦") # Icon Pesanan
        with col3:
            ui_components.display_metric_card("Total Pendapatan", f"Rp{int(total_inc):,}", "💰") # Icon Pendapatan
        
        st.subheader("5 Pesanan Terbaru")
        df_last_orders = om.get_last_five_orders()
        if not df_last_orders.empty:
            st.dataframe(df_last_orders, use_container_width=True)
        else:
            st.info("Belum ada pesanan.")
        
        st.subheader("Produk dengan Stok Rendah")
        threshold = st.number_input("Batas Stok Minimum", min_value=1, value=5, key="low_stock_threshold")
        df_low_stock = pm.get_low_stock_products(threshold)
        if not df_low_stock.empty:
            st.dataframe(df_low_stock, use_container_width=True)
        else:
            st.success("Semua stok produk aman!")

    elif page == "Produk":
        ui_components.show_header("Manajemen Produk")
        tab1, tab2, tab3 = st.tabs(["Daftar Produk", "Update Stok", "Update Harga"])

        # Gunakan indeks dari session_state.active_tab
        tab_idx = tab_names.index(st.session_state.active_tab)

        with tab1:
            st.subheader("Daftar Produk")
            product_list = pm.get_all_products() # Menggunakan dictionary=True dari pm
            if product_list:
                # Membuat 2 kolom untuk tampilan card produk
                cols = st.columns(2)
                for i, product_item in enumerate(product_list):
                    with cols[i % 2]:
                         # Peran admin tidak perlu form pesan, jadi beberapa argumen bisa None atau disesuaikan
                        ui_components.display_product_card(product_item, st.session_state.role, None, None)
            else:
                st.info("Tidak ada produk.")
        
        with tab2:
            st.subheader("Perbarui Stok Bunga")
            bunga_options = {b['bungaName']: b['bungaID'] for b in pm.get_bunga_list()}
            if bunga_options:
                selected_bunga_name = st.selectbox("Pilih Bunga", list(bunga_options.keys()), key="stok_select_bunga")
                selected_bunga_id = bunga_options[selected_bunga_name]
                tambah_stock_val = st.number_input("Jumlah Stock yang Ditambahkan", min_value=1, step=1, key="stok_input_val")
                
                if st.button("Tambah Stock", key="tambah_stok_btn_admin"):
                    if selected_bunga_id and tambah_stock_val > 0:
                        success = pm.update_stock(selected_bunga_id, tambah_stock_val)
                        if success:
                            st.session_state.temp_message = {"type": "success", "text": f"Stok {selected_bunga_name} berhasil ditambah {tambah_stock_val}."}
                        else:
                            st.session_state.temp_message = {"type": "error", "text": "Gagal memperbarui stok."}
                        st.rerun()
            else:
                st.warning("Tidak ada bunga untuk dipilih.")

            with tabs[tab_idx]:
                if st.session_state.active_tab == "Update Harga":
                    st.subheader("Update Harga Bunga")
                
                    # Simulasi bunga list
                    bunga_options_harga = {"Mawar": 1, "Melati": 2}
                    selected_bunga_name_hrg = st.selectbox(
                        "Pilih Bunga",
                        list(bunga_options_harga.keys()),
                        key="harga_select_bunga"
                    )
                    selected_bunga_id_hrg = bunga_options_harga[selected_bunga_name_hrg]
                
                    new_price_val = st.number_input(
                        "Harga Baru per Tangkai",
                        min_value=0.0,
                        step=1000.0,
                        format="%.2f",
                        key="harga_input_val"
                    )
                
                    if st.button("Update Harga", key="update_harga_btn_admin"):
                        # Simulasi update sukses
                        st.session_state.temp_message = {
                            "type": "success",
                            "text": f"Harga {selected_bunga_name_hrg} berhasil diupdate."
                        }
                        # Tetap di tab ini saat rerun
                        st.session_state.active_tab = "Update Harga"
                        st.experimental_rerun()
                
            # Tetapkan tab aktif saat pertama kali di-click
            for i, tab in enumerate(tabs):
                with tab:
                    if st.button(f"Ke {tab_names[i]}", key=f"goto_tab_{i}"):
                        st.session_state.active_tab = tab_names[i]
                        st.experimental_rerun()
                
            # Tampilkan pesan (jika ada)
            if "temp_message" in st.session_state:
                msg = st.session_state.pop("temp_message")
                if msg["type"] == "success":
                    st.success(msg["text"])

    elif page == "Pelanggan":
        ui_components.show_header("Manajemen Pelanggan")
        tab1, tab2 = st.tabs(["Daftar Pelanggan", "Hapus Pelanggan"])

        with tab1:
            st.subheader("Daftar Pelanggan")
            search_query_cust = st.text_input("Cari Pelanggan (Nama/Email)", "", key="cust_search_admin")
            cust_id_search = st.text_input("Cari berdasarkan ID Pelanggan", "", key="cust_id_search_admin")
            df_customers = cm.get_customers(search_query_cust, cust_id_search)
            st.dataframe(df_customers, use_container_width=True)

        with tab2:
            st.subheader("Hapus Pelanggan")
            cust_id_to_delete = st.number_input("ID Pelanggan yang akan dihapus", min_value=1, step=1, key="cust_delete_id_admin")
            if st.button("Hapus Pelanggan", type="primary", key="delete_cust_btn_admin"):
                if cust_id_to_delete:
                    result = cm.delete_customer(cust_id_to_delete)
                    st.session_state.temp_message = {"type": "success" if result["success"] else "error", "text": result["message"]}
                    st.rerun()

    elif page == "Pesanan":
        ui_components.show_header("Manajemen Pesanan")
        # Implementasi tab-tab pesanan untuk Admin (Buat Pesanan, Riwayat, Update Status, dll.)
        # ... (Mirip dengan kode asli Anda, tapi panggil fungsi dari om.* dan cm.*) ...
        # Contoh:
        tab_pesanan_admin1, tab_pesanan_admin2, tab_pesanan_admin3 = st.tabs([
            "Pesanan Pelanggan", "Daftar Semua Pesanan", "Detail Pesanan"
        ])

        with tab_pesanan_admin1:
            subtab1, subtab2, subtab3, subtab4 = st.tabs(["Buat Pesanan", "Riwayat Pesanan", "Informasi Pesanan", "Update Status"])

            with subtab1:
                st.subheader("Buat Pesanan Baru")
                custID = st.number_input("Customer ID", min_value=1, step=1, key="customer_new_order")
                paymentMethod = st.selectbox("Metode Pembayaran", ["Cash", "OVO", "Gopay", "Dana"])
                bunga_list = pm.get_bunga_list()
                bunga_names = {b['bungaName']: b['bungaID'] for b in pm.get_bunga_list()}
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
                    df_cust_orders = om.get_customer_orders_history(custID)
                    if not df_cust_orders.empty:
                        st.dataframe(df_cust_orders, use_container_width=True)
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
                st.subheader("Perbarui Status Pesanan")
                order_id_update = st.number_input("Order ID untuk Update Status", min_value=1, step=1, key="admin_order_id_update")
                new_status = st.selectbox("Status Baru", ["Processed", "Shipped", "Completed", "Cancelled"], key="admin_new_status_select")
                if st.button("Update Status", key="admin_update_status_btn"):
                    if order_id_update and new_status:
                        success = om.update_order_status(order_id_update, new_status)
                        if success:
                            st.session_state.temp_message = {"type": "success", "text": f"Status pesanan {order_id_update} berhasil diupdate menjadi {new_status}."}
                        else:
                            st.session_state.temp_message = {"type": "error", "text": f"Gagal mengupdate status pesanan {order_id_update}."}
                        st.rerun()

        with tab_pesanan_admin2:
            st.subheader("Daftar Semua Pesanan")
            search_order_id = st.text_input("Cari Order ID", "", key="admin_search_order_id")
            status_filter = st.selectbox("Filter Status", ["", "Processed", "Shipped", "Completed", "Cancelled"], key="admin_status_filter")
            order_date_filter = st.date_input("Filter Tanggal Pesanan", value=None, key="admin_date_filter")
            payment_method_filter = st.selectbox("Filter Metode Pembayaran", ["", "Cash", "OVO", "Gopay", "Dana"], key="admin_payment_filter")
            
            df_orders = om.get_orders(search_order_id, status_filter, order_date_filter, payment_method_filter)
            st.dataframe(df_orders, use_container_width=True)

        with tab_pesanan_admin3:
            st.subheader("Lihat Detail Pesanan")
            admin_order_id_detail = st.text_input("Masukkan Order ID untuk Detail", key="admin_order_id_detail_input")
            admin_cust_id_detail = st.number_input("Masukkan Customer ID Pemilik Pesanan", min_value=1, step=1, key="admin_cust_id_detail_input")
            if st.button("Tampilkan Detail", key="admin_show_detail_btn"):
                if admin_order_id_detail and admin_cust_id_detail:
                    details = om.get_full_order_details_for_customer(admin_order_id_detail, admin_cust_id_detail)
                    if details:
                        ui_components.show_order_details_component(details)
                    else:
                        st.warning("Detail pesanan tidak ditemukan atau ID tidak cocok.")
                else:
                    st.warning("Mohon masukkan Order ID dan Customer ID.")


    elif page == "Laporan Penjualan":
        ui_components.show_header("Laporan Penjualan")
        # Implementasi tab-tab laporan (Produk Terlaris, Pendapatan)
        # ... (Mirip dengan kode asli Anda, tapi panggil fungsi dari reporting.*) ...
        tab_laporan1, tab_laporan2 = st.tabs(["Produk Terlaris", "Analisis Pendapatan"])

        with tab_laporan1:
            st.subheader("Produk Bunga Terlaris")
            df_top_products = pm.get_top_selling_products()
            if not df_top_products.empty:
                fig, ax = plt.subplots()
                ax.bar(df_top_products["Nama Bunga"], df_top_products["Total Terjual"], color='#ff6b6b')
                ax.set_xlabel("Nama Bunga")
                ax.set_ylabel("Jumlah Terjual")
                ax.set_title("Produk Bunga Terlaris")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("Belum ada data penjualan untuk ditampilkan.")
        
        with tab_laporan2:
            st.subheader("Pendapatan Berdasarkan Rentang Tanggal")
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input("Tanggal Mulai", key="report_start_date")
            with col_date2:
                end_date = st.date_input("Tanggal Selesai", key="report_end_date")
            
            if st.button("Hitung Pendapatan Rentang Ini", key="calc_income_range_btn"):
                if start_date and end_date and start_date <= end_date:
                    total_income_range = reporting.get_income_between_dates(start_date, end_date)
                    st.metric(label="Total Pendapatan pada Rentang Terpilih", value=f"Rp{total_income_range:,.0f}")
                else:
                    st.warning("Pastikan tanggal mulai tidak melebihi tanggal selesai.")

            st.subheader("Grafik Pendapatan Bulanan")
            df_monthly_revenue = reporting.get_monthly_revenue()
            if not df_monthly_revenue.empty:
                fig_monthly, ax_monthly = plt.subplots()
                ax_monthly.plot(df_monthly_revenue["Bulan"], df_monthly_revenue["Pendapatan"], marker='o', linestyle='-', color='#ff6b6b')
                ax_monthly.set_xlabel("Bulan (YYYY-MM)")
                ax_monthly.set_ylabel("Pendapatan (Rp)")
                ax_monthly.set_title("Tren Pendapatan Bulanan")
                plt.xticks(rotation=45, ha="right")
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                st.pyplot(fig_monthly)
            else:
                st.info("Belum ada data pendapatan bulanan.")


# == HALAMAN CUSTOMER ==
elif st.session_state.role == 'customer':
    current_cust_username = st.session_state.username
    current_cust_id = auth.extract_cust_id_from_username(current_cust_username)

    if page == "Produk":
        ui_components.show_header(f"Selamat Datang, Customer!")
        st.subheader("Produk Terpopuler Kami")
        product_list_cust = pm.get_all_products()
        if product_list_cust:
            # Membuat 2 kolom untuk tampilan card produk
            cols_cust_prod = st.columns(2)
            for i, product_item_data in enumerate(product_list_cust):
                with cols_cust_prod[i % 2]:
                    ui_components.display_product_card(
                        product_item_data,
                        st.session_state.role,
                        auth.extract_cust_id_from_username,
                        om.create_new_order
                    )
        else:
            st.info("Tidak ada produk yang tersedia saat ini.")


    elif page == "Pesanan Saya":
        ui_components.show_header("Riwayat Pesanan Anda")
        if current_cust_id:
            tab_cust_order1, tab_cust_order2, tab_cust_order3 = st.tabs([
                "Semua Pesanan Saya", "Lihat Detail Pesanan", "Batalkan Pesanan"
            ])

            with tab_cust_order1:
                st.subheader("Daftar Pesanan Anda")
                df_cust_orders = om.get_customer_orders_history(current_cust_id)
                if not df_cust_orders.empty:
                    st.dataframe(df_cust_orders, use_container_width=True)
                else:
                    st.info("Anda belum memiliki riwayat pesanan.")
            
            with tab_cust_order2:
                st.subheader("Detail Pesanan Spesifik")
                order_id_to_view = st.text_input("Masukkan Order ID yang ingin dilihat:", key="cust_view_order_id")
                if st.button("Tampilkan Detail Pesanan", key="cust_show_detail_btn"):
                    if order_id_to_view:
                        order_details_data = om.get_full_order_details_for_customer(order_id_to_view, current_cust_id)
                        if order_details_data:
                            ui_components.show_order_details_component(order_details_data)
                        else:
                            st.warning("Order ID tidak ditemukan atau bukan milik Anda.")
                    else:
                        st.warning("Mohon masukkan Order ID.")

            with tab_cust_order3:
                st.subheader("Batalkan Pesanan")
                order_id_to_cancel = st.text_input("Masukkan Order ID yang ingin dibatalkan:", key="cust_cancel_order_id")
                if st.button("Ajukan Pembatalan", type="primary", key="cust_cancel_btn"):
                    if order_id_to_cancel:
                        cancel_result = om.cancel_order(order_id_to_cancel, current_cust_id)
                        st.session_state.temp_message = {"type": "success" if cancel_result["success"] else "error", "text": cancel_result["message"]}
                        st.rerun()
                    else:
                        st.warning("Mohon masukkan Order ID.")
        else:
            st.error("Tidak dapat memuat data pesanan. Customer ID tidak valid.")


    elif page == "Informasi Akun":
        ui_components.show_header("Informasi Akun Saya")
        if current_cust_id:
            tab_akun1, tab_akun2 = st.tabs(["Profil Saya", "Ganti Password"])
            with tab_akun1:
                st.subheader("Detail Profil")
                customer_profile = cm.get_customer_info(current_cust_id)
                if customer_profile:
                    st.text_input("Nama Depan", value=customer_profile.get('firstName', ''), disabled=True)
                    st.text_input("Nama Belakang", value=customer_profile.get('lastName', ''), disabled=True)
                    st.text_input("Email", value=customer_profile.get('email', ''), disabled=True)
                    st.text_input("Nomor Telepon", value=customer_profile.get('phoneNumber', ''), disabled=True)
                    st.text_area("Alamat", value=customer_profile.get('address', ''), disabled=True)
                    st.text_input("Username", value=customer_profile.get('username', ''), disabled=True)
                else:
                    st.error("Gagal mengambil data profil.")
            
            with tab_akun2:
                st.subheader("Ganti Password")
                with st.form("change_password_form_customer"):
                    old_pass = st.text_input("Password Lama", type="password")
                    new_pass = st.text_input("Password Baru", type="password")
                    confirm_pass = st.text_input("Konfirmasi Password Baru", type="password")
                    submitted_pass_change = st.form_submit_button("Ganti Password")

                    if submitted_pass_change:
                        if not all([old_pass, new_pass, confirm_pass]):
                            st.warning("Semua field password harus diisi.")
                        elif new_pass != confirm_pass:
                            st.error("Password baru dan konfirmasi password tidak cocok.")
                        else:
                            if auth.verify_old_password(current_cust_username, old_pass):
                                if auth.update_password(current_cust_username, new_pass):
                                    st.session_state.temp_message = {"type": "success", "text": "Password berhasil diganti!"}
                                else:
                                    st.session_state.temp_message = {"type": "error", "text": "Gagal mengganti password di database."}
                            else:
                                st.error("Password lama salah.")
                            st.rerun() # Untuk menampilkan pesan
        else:
            st.error("Tidak dapat memuat informasi akun. Customer ID tidak valid.")
