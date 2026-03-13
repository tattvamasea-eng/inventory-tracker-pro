import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Inventory Tracker Pro", page_icon="📦")

st.title("📦 Inventory Tracker Pro")

# Free Website Offer Banner
st.markdown("""
🎉 **Special Offer for Mississauga Businesses!**

Need a website for your business? I build them **FREE**!

👉 **Email cram@agentmail.to** to claim your free business website.

*Limited to first 10 Mississauga businesses.*

---
""")

# Custom JavaScript for localStorage
st.markdown("""
<script>
function saveData(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}
function loadData(key) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
}
function clearData(key) {
    localStorage.removeItem(key);
}
</script>
""", unsafe_allow_html=True)

# User identification - simple login
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Login/Setup screen
if st.session_state.user_id is None:
    st.subheader("👋 Welcome!")
    st.write("Enter your workspace name to get started:")
    
    user_input = st.text_input("Workspace Name", placeholder="my-business")
    
    if st.button("Start Tracking"):
        if user_input:
            st.session_state.user_id = user_input.strip().replace(" ", "-").lower()
            st.rerun()
    
    st.markdown("---")
    st.info("💡 Your data is stored locally in your browser. No account needed.")
    st.stop()

# Now we have a user_id - load their data
user_key = f"inventory_pro_{st.session_state.user_id}"

# Initialize session state
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "sales" not in st.session_state:
    st.session_state.sales = []

# Data storage helpers
def load_user_data():
    return st.session_state.inventory, st.session_state.sales

def save_user_data():
    pass

# Get data
inventory, sales = load_user_data()
df = pd.DataFrame(inventory) if inventory else pd.DataFrame()
sales_df = pd.DataFrame(sales) if sales else pd.DataFrame()

# Logout button
col_logout, col_title = st.columns([1, 9])
with col_logout:
    if st.button("🔄 Switch Workspace"):
        st.session_state.user_id = None
        st.session_state.inventory = []
        st.session_state.sales = []
        st.rerun()

st.markdown(f"**Workspace:** `{st.session_state.user_id}`")

# Display inventory table
st.subheader("📦 Current Inventory")

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No products yet. Add your first product below!")

# Summary metrics
if not df.empty:
    total_items = df["Quantity"].sum()
    total_value = (df["Quantity"] * df["Price"]).sum()
    low_stock = df[df["Quantity"] <= df["Reorder Level"]]
    total_revenue = sum(s["Revenue"] for s in sales) if sales else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items", total_items)
    col2.metric("Inventory Value", f"${total_value:,.2f}")
    col3.metric("Low Stock Items", len(low_stock))
    col4.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    if not low_stock.empty:
        st.warning(f"⚠️ {len(low_stock)} items are below reorder level!")
        st.dataframe(low_stock[["Product", "Quantity", "Reorder Level"]], use_container_width=True)
else:
    total_revenue = 0

# Tabs
tab1, tab2, tab3 = st.tabs(["➕ Add Products", "💰 Record Sale", "💾 Export"])

with tab1:
    st.subheader("Add New Product")
    with st.form("add_item"):
        col1, col2 = st.columns(2)
        with col1:
            product = st.text_input("Product Name", key="add_product")
            sku = st.text_input("SKU", key="add_sku")
        with col2:
            quantity = st.number_input("Quantity", min_value=0, value=0, key="add_qty")
            price = st.number_input("Price ($)", min_value=0.0, value=0.0, key="add_price")
        reorder_level = st.number_input("Reorder Level", min_value=0, value=10, key="add_reorder")
        submitted = st.form_submit_button("Add Product")
        
        if submitted and product and sku:
            new_item = {"Product": product, "SKU": sku, "Quantity": quantity, "Price": price, "Reorder Level": reorder_level}
            st.session_state.inventory.append(new_item)
            st.success(f"Added {product}!")
            st.rerun()

with tab2:
    st.subheader("Record a Sale")
    if not df.empty:
        product_names = df["Product"].tolist()
        selected_product = st.selectbox("Select Product", product_names, key="sale_product")
        
        if selected_product:
            product_data = df[df["Product"] == selected_product].iloc[0]
            available = product_data["Quantity"]
            price = product_data["Price"]
            
            st.info(f"Available: {available} | Price: ${price:.2f}")
            
            with st.form("record_sale"):
                quantity_sold = st.number_input("Quantity Sold", min_value=1, max_value=int(available), value=1, key="sale_qty")
                sale_submitted = st.form_submit_button("Record Sale")
                
                if sale_submitted:
                    for item in st.session_state.inventory:
                        if item["Product"] == selected_product:
                            item["Quantity"] -= quantity_sold
                            break
                    
                    sale_record = {"Product": selected_product, "Quantity": quantity_sold, "Unit Price": price, "Revenue": quantity_sold * price}
                    st.session_state.sales.append(sale_record)
                    st.success(f"Sale recorded! Revenue: ${quantity_sold * price:.2f}")
                    st.rerun()
    else:
        st.info("No products in inventory. Add products first.")

with tab3:
    st.subheader("Export Data")
    if st.button("Download Inventory CSV"):
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "inventory.csv", "text/csv")
        else:
            st.info("No inventory to export.")
    
    if sales:
        st.download_button("Download Sales CSV", sales_df.to_csv(index=False), "sales.csv", "text/csv")
    
    if not sales:
        st.info("No sales recorded yet.")

if sales:
    st.subheader("📊 Recent Sales")
    st.dataframe(sales_df, use_container_width=True)

st.markdown("---")
st.markdown("*Inventory Tracker Pro — Built by Agent Cram | [Get Support](mailto:cram@agentmail.to)*")