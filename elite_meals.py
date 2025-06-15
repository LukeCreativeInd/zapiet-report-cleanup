# elite_meals.py

import pandas as pd
import io
import streamlit as st

def run_elite_meals_flow(df, mapping_df):
    # Hardcoded product order from app.py
    meal_order = [
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
        "Baked Family Lasagna"
    ]

    # Create mapping
    mapping = dict(zip(mapping_df["Report Mapping Name"], mapping_df["Elite Meals Meals"]))

    # Normalize and map
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={"product name": "Product"}, inplace=True)

    df["Standardized Meal"] = df["Product"].replace(mapping)
    df["Standardized Meal"] = df["Standardized Meal"].fillna(df["Product"])

    # Group
    grouped = df.groupby("Standardized Meal", as_index=False)["quantity"].sum()

    # Ensure full meal order appears with 0s if missing
    full_df = pd.DataFrame({"Standardized Meal": meal_order})
    merged = pd.merge(full_df, grouped, on="Standardized Meal", how="left").fillna(0)
    merged["quantity"] = merged["quantity"].astype(int)

    # Rename for display
    merged.rename(columns={"Standardized Meal": "Product name", "quantity": "Quantity"}, inplace=True)

    # Display
    st.subheader("Summary Table")
    st.dataframe(merged, use_container_width=True)

    # Download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        merged.to_excel(writer, index=False, sheet_name='Summary')
    buffer.seek(0)

    st.download_button(
        label="Download Summary as Excel",
        data=buffer,
        file_name="elite_meals_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
