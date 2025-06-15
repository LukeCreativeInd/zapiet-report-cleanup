# elite_meals.py

import pandas as pd
import io
import streamlit as st

def run_elite_meals_flow(df):
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
        "Family Mac and 3 Cheese Pasta Bake",
        "Baked Family Lasagna",
        "Steak On Its Own",
        "Chicken On Its Own"
    ]

    # Hardcoded mapping
    mapping = {
        "Beef Burrito Bowl": "Beef Burrito Bowl",
        "Beef Chow Mein With Rice": "Beef Chow Mein",
        "Butter Chicken With Basmati Rice": "Butter Chicken",
        "Chicken Pesto Pasta": "Chicken Pesto Pasta",
        "Chicken with Vegetables": "Chicken with Vegetables",
        "Chicken with Sweet Potato and Beans": "Chicken with Sweet Potato and Beans",
        "Naked Chicken Parma": "Naked Chicken Parma",
        "Chicken Fajita Bowl": "Chicken Fajita Bowl",
        "Creamy Chicken & Mushroom Gnocchi": "Creamy Chicken & Mushroom Gnocchi",
        "Roasted Lemon Chicken & Potatoes": "Roasted Lemon Chicken & Potatoes",
        "Soulfood Lasagna": "Beef Lasagna",
        "Bean Nachos with Rice": "Bean Nachos with Rice",
        "Lamb Souvlaki Plate": "Lamb Souvlaki",
        "Steak & Mash with Mushroom Sauce": "Steak with Mushroom Sauce",
        "Spaghetti Bolognese": "Spaghetti Bolognese",
        "Moroccan Chicken with Rice": "Moroccan Chicken",
        "Thai Green Chicken Curry with Rice": "Thai Green Chicken Curry",
        "Shepherd's Pie": "Shepherd's Pie",
        "Chicken On Its Own": "Chicken On Its Own",
        "Steak On Its Own": "Steak On Its Own",
        "Family Mac and 3 Cheese Pasta Bake": "Family Mac and 3 Cheese Pasta Bake",
        "Baked Family Lasagna": "Baked Family Lasagna",
        "Chicken and Broccoli Pasta": "Chicken and Broccoli Pasta",
        "Lebanese Beef Stew": "Lebanese Beef Stew",
        "Mongolian Beef Stir Fry": "Mongolian Beef",
        "Beef Meatballs in Napolitana Sauce": "Beef Meatballs"
    }

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
