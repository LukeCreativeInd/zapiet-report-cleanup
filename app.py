import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Product Quantity Summary", layout="centered")
st.title("Product Quantity Summary")
st.markdown("Upload your Zapiet export to see a total quantity summary grouped by product name.")

# Final product order (must match uploaded CSV exactly)
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
    "Baked Family Lasagna"
]

uploaded_file = st.file_uploader("Upload Zapiet Production Report CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "Product name" in df.columns and "Quantity" in df.columns:
        # Group and sum the uploaded data
        summary_df = df.groupby("Product name", as_index=False)["Quantity"].sum()

        # Ensure all products are listed in your defined order with 0s if missing
        full_df = pd.DataFrame({"Product name": product_order})
        summary_df = pd.merge(full_df, summary_df, on="Product name", how="left").fillna(0)
        summary_df["Quantity"] = summary_df["Quantity"].astype(int)

        st.subheader("Summary Table")
        st.dataframe(summary_df, use_container_width=True)

        # Create downloadable Excel file
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
