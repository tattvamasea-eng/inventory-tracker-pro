import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Inventory Tracker Pro", page_icon="📦")

st.title("📦 Inventory Tracker Pro")

# Initialize session state for data
if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"Product": "Widget A", "SKU": "WGT-001", "Quantity": 100, "Price": 19.99, "Reorder Level": 20},
        {"Product": "Widget B", "SKU": "WGT-002", "Quantity": 50, "Price": 29.99, "Reorder Level": 15},
        {"Product": "Gadget X", "SKU": "GDG-101", "Quantity": 200, "Price": 9.99, "Reorder Level": 50},
    ]

if "sales" not in st.session_state:
    st.session_state.sales = []

# Convert to DataFrame
df = pd.DataFrame(st.session_state.inventory)
sales_df = pd.DataFrame(st.session_state.sales) if st.session_state.sales else pd.DataFrame()

# Display inventory table
st.subheader("📦 Current Inventory")
st.dataframe(df, use_container_width=True)

# Summary metrics
total_items = df["Quantity"].sum()
total_value = (df["Quantity"] * df["Price"]).sum()
low_stock = df[df["Quantity"] <= df["Reorder Level"]]
total_revenue = sum(s["Revenue"] for s in st.session_state.sales) if st.session_state.sales else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Items", total_items)
col2.metric("Inventory Value", f"${total_value:,.2f}")
col3.metric("Low Stock Items", len(low_stock))
col4.metric("Total Revenue", f"${total_revenue:,.2f}")

# Low stock alert
if not low_stock.empty:
    st.warning(f"⚠️ {len(low_stock)} items are below reorder level!")
    st.dataframe(low_stock[["Product", "Quantity", "Reorder Level"]], use_container_width=True)

# Tabs for different functions
tab1, tab2, tab3 = st.tabs(["➕ Add Products", "💰 Record Sale", "💾 Export"])

with tab1:
    st.subheader("Add New Product")
    with st.form("add_item"):
        col1, col2 = st.columns(2)
        with col1:
            product = st.text_input("Product Name")
            sku = st.text_input("SKU")
        with col2:
            quantity = st.number_input("Quantity", min_value=0, value=0)
            price = st.number_input("Price ($)", min_value=0.0, value=0.0)
        reorder_level = st.number_input("Reorder Level", min_value=0, value=10)
        submitted = st.form_submit_button("Add Product")
        
        if submitted and product and sku:
            new_item = {
                "Product": product,
                "SKU": sku,
                "Quantity": quantity,
                "Price": price,
                "Reorder Level": reorder_level
            }
            st.session_state.inventory.append(new_item)
            st.success(f"Added {product}!")
            st.rerun()

with tab2:
    st.subheader("Record a Sale")
    if df.empty:
        st.info("No products in inventory. Add products first.")
    else:
        product_names = df["Product"].tolist()
        selected_product = st.selectbox("Select Product", product_names)
        
        if selected_product:
            product_data = df[df["Product"] == selected_product].iloc[0]
            available = product_data["Quantity"]
            price = product_data["Price"]
            
            st.info(f"Available: {available} | Price: ${price:.2f}")
            
            with st.form("record_sale"):
                quantity_sold = st.number_input("Quantity Sold", min_value=1, max_value=int(available), value=1)
                sale_submitted = st.form_submit_button("Record Sale")
                
                if sale_submitted:
                    # Find and update inventory
                    for item in st.session_state.inventory:
                        if item["Product"] == selected_product:
                            item["Quantity"] -= quantity_sold
                            break
                    
                    # Record the sale
                    sale_record = {
                        "Product": selected_product,
                        "Quantity": quantity_sold,
                        "Unit Price": price,
                        "Revenue": quantity_sold * price
                    }
                    st.session_state.sales.append(sale_record)
                    
                    st.success(f"Sale recorded! Revenue: ${quantity_sold * price:.2f}")
                    st.rerun()

with tab3:
    st.subheader("Export Data")
    if st.button("Download Inventory CSV"):
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "inventory.csv", "text/csv")
    
    if st.session_state.sales:
        sales_csv = sales_df.to_csv(index=False)
        st.download_button("Download Sales CSV", sales_csv, "sales.csv", "text/csv")
    
    if not st.session_state.sales:
        st.info("No sales recorded yet.")

# Sales history
if st.session_state.sales:
    st.subheader("📊 Recent Sales")
    st.dataframe(sales_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("*Inventory Tracker Pro — Built by Agent Cram | [Get Support](mailto:cram@agentmail.to)*")