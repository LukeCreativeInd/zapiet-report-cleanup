import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Product Quantity Summary", layout="centered")
st.title("Product Quantity Summary")
st.markdown("Upload your Zapiet export to see a total quantity summary grouped by product name.")

uploaded_file = st.file_uploader("Upload Zapiet Production Report CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "Product name" in df.columns and "Quantity" in df.columns:
        # Group by Product name and sum Quantity
        summary_df = df.groupby("Product name", as_index=False)["Quantity"].sum()
        summary_df = summary_df.sort_values(by="Quantity", ascending=False)

        st.subheader("Summary Table")
        st.dataframe(summary_df, use_container_width=True)

        # Create download button for Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            summary_df.to_excel(writer, index=False, sheet_name='Summary')
        buffer.seek(0)

        st.download_button(
            label="Download Summary as Excel",
            data=buffer,
            file_name="product_quantity_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.error("CSV must contain 'Product name' and 'Quantity' columns.")
