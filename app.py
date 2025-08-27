import streamlit as st
import pandas as pd

from clean_eats import run_clean_eats_flow
from made_active import run_made_active_flow
from elite_meals import run_elite_meals_flow

# --- CONFIG ---
st.set_page_config(page_title="Product Quantity Summary", layout="centered")

# --- CLIENT SELECTOR ---
selected_client = st.radio("Select Client", ["Clean Eats", "Made Active", "Elite Meals"], horizontal=True)

# --- PRODUCT ORDER (shared across clients that use ordering) ---
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
    "Steak On Its Own",
    "Chicken On Its Own",
    "Family Mac and 3 Cheese Pasta Bake",
    "Baked Family Lasagna",
]

def _read_upload(uploaded_file):
    if uploaded_file is None:
        return None
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload a CSV or Excel file.")
        return None

# --- FILE UPLOAD UI ---
if selected_client == "Clean Eats":
    st.markdown("**Upload one or two Zapiet Production Report files. The second file is optional.**")
    ce_file_1 = st.file_uploader("Clean Eats – File 1 (CSV or Excel)", type=["csv", "xlsx"], key="ce1")
    ce_file_2 = st.file_uploader("Clean Eats – File 2 (Optional)", type=["csv", "xlsx"], key="ce2")
    generate = st.button("Generate Report")

    if generate:
        if not ce_file_1 and not ce_file_2:
            st.error("Please upload at least one file for Clean Eats.")
        else:
            # Read whichever files are provided
            df_list = []
            for f in (ce_file_1, ce_file_2):
                df = _read_upload(f)
                if df is not None:
                    df_list.append(df)

            # Concatenate if two provided; otherwise just use the one
            combined_df = pd.concat(df_list, ignore_index=True) if len(df_list) > 1 else df_list[0]

            st.success("File(s) uploaded. Running script for **Clean Eats**...")
            st.subheader("Raw Data Preview")
            st.dataframe(combined_df.head(), use_container_width=True)

            # Validate required columns
            required_cols = {"Product name", "Quantity"}
            if not required_cols.issubset(set(combined_df.columns)):
                st.error("File(s) must contain 'Product name' and 'Quantity' columns.")
            else:
                run_clean_eats_flow(combined_df, product_order)

elif selected_client == "Made Active":
    ma_file = st.file_uploader("Upload Zapiet Production Report (CSV or Excel)", type=["csv", "xlsx"], key="ma")
    generate = st.button("Generate Report")

    if generate:
        if not ma_file:
            st.error("Please upload a file to continue.")
        else:
            df = _read_upload(ma_file)
            if df is not None:
                st.success("File uploaded. Running script for **Made Active**...")
                st.subheader("Raw Data Preview")
                st.dataframe(df.head(), use_container_width=True)

                if "Product name" not in df.columns or "Quantity" not in df.columns:
                    st.error("File must contain 'Product name' and 'Quantity' columns.")
                else:
                    run_made_active_flow(df, product_order)

elif selected_client == "Elite Meals":
    em_file = st.file_uploader("Upload Zapiet Production Report (CSV or Excel)", type=["csv", "xlsx"], key="em")
    generate = st.button("Generate Report")

    if generate:
        if not em_file:
            st.error("Please upload a file to continue.")
        else:
            df = _read_upload(em_file)
            if df is not None:
                st.success("File uploaded. Running script for **Elite Meals**...")
                st.subheader("Raw Data Preview")
                st.dataframe(df.head(), use_container_width=True)

                if "Product name" not in df.columns or "Quantity" not in df.columns:
                    st.error("File must contain 'Product name' and 'Quantity' columns.")
                else:
                    run_elite_meals_flow(df)
