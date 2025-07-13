# clean_eats.py

import pandas as pd
import io
import streamlit as st

def run_clean_eats_flow(df, product_order):
    # Only keep rows where the product is in product_order
    grouped = df[df["Product name"].isin(product_order)].groupby("Product name", as_index=False)["Quantity"].sum()
    
    # Ensure all products in product_order are present in the final table (zero if not ordered)
    full_df = pd.DataFrame({"Product name": product_order})
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
