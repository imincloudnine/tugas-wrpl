# ✅ Refactored Functions to Supabase SDK

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

def get_customer_orders(custID):
    response = supabase.table("orders").select("*").eq("custID", custID).order("orderDate", desc=True).execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def update_order_status(orderID, newStatus):
    response = supabase.table("orders").update({"status": newStatus}).eq("orderID", orderID).execute()
    return response.data is not None

def update_stock(bungaID, tambahStock):
    # Get current stock
    res = supabase.table("products").select("stock").eq("bungaID", bungaID).single().execute()
    if res.data:
        current_stock = res.data["stock"]
        new_stock = current_stock + tambahStock
        update_res = supabase.table("products").update({"stock": new_stock}).eq("bungaID", bungaID).execute()
        if update_res.data:
            st.success(f"Stok bunga berhasil ditambahkan sebanyak {tambahStock} tangkai!")

def get_top_selling_products():
    response = supabase.rpc("top_selling_products").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["Nama Bunga", "Total Terjual"])

def get_customers(search_query=""):
    query = supabase.table("customers").select("*")
    if search_query:
        query = query.ilike("firstName", f"%{search_query}%")
    result = query.execute()
    return pd.DataFrame(result.data) if result.data else pd.DataFrame()

def delete_customer(custID):
    supabase.table("customers").delete().eq("custID", custID).execute()
    username = f"customer{custID}"
    supabase.table("users").delete().eq("username", username).execute()
    st.success(f"Customer ID {custID} dan user '{username}' berhasil dihapus!")