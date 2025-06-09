import streamlit as st
import pandas as pd
import io

from clean_eats import run_clean_eats_flow
# from made_active import run_made_active_flow (we'll build this next)

st.set_page_config(page_title="Product Quantity Summary", layout="centered")

selected_client = st.radio("Select Client", ["Clean Eats", "Made Active"], horizontal=True)

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
                st.info("Made Active logic will be added next.")

    except Exception as e:
        st.error(f"Error reading file: {e}")
