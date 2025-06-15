# elite_meals.py

import pandas as pd
import io
import streamlit as st

def run_elite_meals_flow(df, mapping_df):
    # Create mapping
    mapping = dict(zip(mapping_df["Report Mapping Name"], mapping_df["Elite Meals Meals"]))
    meal_order = mapping_df["Elite Meals Meals"].tolist()

    # Normalize and map
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={"product name": "Product"}, inplace=True)

    df["Standardized Meal"] = df["Product"].replace(mapping)
    df["Standardized Meal"] = df["Standardized Meal"].fillna(df["Product"])

    # Group
    grouped = df.groupby("Standardized Meal", as_index=False)["quantity"].sum()
    known_set = set(meal_order)
    uploaded_set = set(grouped["Standardized Meal"])
    extras = list(uploaded_set - known_set)

    final_order = meal_order + sorted(extras)

    full_df = pd.DataFrame({"Standardized Meal": final_order})
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
