import streamlit as st
import pandas as pd
import io

# --- CONFIG ---
st.set_page_config(page_title="Product Quantity Summary", layout="centered")

# --- SELECT CLIENT ---
selected_client = st.radio("Select Client", ["Clean Eats", "Made Active"], horizontal=True)

# --- PRODUCT ORDER (SHARED FOR NOW) ---
product_order = [
    "Spaghetti Bolognese",
    "Beef Chow Mein",
    "Shepherd's Pie",
    "Beef Burrito Bowl",
    "Beef Meatballs",
    "Lebanese Beef Stew",
    "Mongolian Beef",
    "Chicken with Vegetables",
    "Chicken with Sweet Potato and Beans",
    "Naked Chicken Parma",
    "Chicken Pesto Pasta",
    "Chicken and Broccoli Pasta",
    "Butter Chicken",
    "Thai Green Chicken Curry",
    "Moroccan Chicken",
    "Steak with Mushroom Sauce",
    "Creamy Chicken & Mushroom Gnocchi",
    "Roasted Lemon Chicken & Potatoes",
    "Beef Lasagna",
    "Bean Nachos with Rice",
    "Lamb Souvlaki",
    "Chicken Fajita Bowl",
    "Family Mac and 3 Cheese Pasta Bake",
    "Baked Family Lasagna",
    "Steak On Its Own",
    "Chicken On Its Own"
]

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload Zapiet Production Report CSV", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"File uploaded. Running script for **{selected_client}**...")
        st.subheader("Raw Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        if "Product name" not in df.columns or "Quantity" not in df.columns:
            st.error("CSV must contain 'Product name' and 'Quantity' columns.")
        else:
            if selected_client == "Clean Eats":
                run_clean_eats_flow(df, product_order)

            elif selected_client == "Made Active":
                run_made_active_flow(df, product_order)

    except Exception as e:
        st.error(f"Error reading file: {e}")

# --- CLEAN EATS FUNCTION ---
def run_clean_eats_flow(df, product_order):
    grouped = df.groupby("Product name", as_index=False)["Quantity"].sum()

    known_set = set(product_order)
    uploaded_set = set(grouped["Product name"])
    extras = list(uploaded_set - known_set)

    final_order = product_order + sorted(extras)

    full_df = pd.DataFrame({"Product name": final_order})
    merged = pd.merge(full_df, grouped, on="Product name", how="left").fillna(0)
    merged["Quantity"] = merged["Quantity"].astype(int)

    st.subheader("Summary Table")
    st.dataframe(merged, use_container_width=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        merged.to_excel(writer, index=False, sheet_name='Summary')
    buffer.seek(0)

    st.download_button(
        label="Download Summary as Excel",
        data=buffer,
        file_name="product_quantity_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- MADE ACTIVE PLACEHOLDER ---
def run_made_active_flow(df, product_order):
    st.info("Bundle unpacking logic for Made Active will be implemented next.")
