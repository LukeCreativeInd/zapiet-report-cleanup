import pandas as pd
import io
import streamlit as st

# Name normalization mapping
name_map = {
    "Chicken with Broccoli & Beans": "Chicken with Vegetables",
    "Butter Chicken with Basmati Rice": "Butter Chicken",
    "Baked Chicken Breast": "Chicken On Its Own",
    "Porterhouse Steak": "Steak On Its Own"
}

def run_made_active_flow(df, product_order):
    # Apply name mapping
    df["Product name"] = df["Product name"].replace(name_map)

    # Group and sum
    grouped = df.groupby("Product name", as_index=False)["Quantity"].sum()

    # Include all ordered items and extras
    known_set = set(product_order)
    uploaded_set = set(grouped["Product name"])
    extras = list(uploaded_set - known_set)
    final_order = product_order + sorted(extras)

    full_df = pd.DataFrame({"Product name": final_order})
    merged = pd.merge(full_df, grouped, on="Product name", how="left").fillna(0)
    merged["Quantity"] = merged["Quantity"].astype(int)

    # Output
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
