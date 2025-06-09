import streamlit as st
import pandas as pd
import io

# Set page config
st.set_page_config(page_title="Product Quantity Summary", layout="centered")

# Sidebar selector
client = st.sidebar.selectbox("Select Client", ["Clean Eats", "Made Active"])

# Page header
st.title(f"Product Quantity Summary – {client}")
st.markdown("Upload your Zapiet export to see a total quantity summary grouped by product name.")

# Product order for both clients (same order assumed for now)
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
    st.success(f"File uploaded. Processing for **{client}**…")

    try:
        df = pd.read_csv(uploaded_file)

        # Preview raw file
        st.subheader("Raw Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        if "Product name" not in df.columns or "Quantity" not in df.columns:
            st.error("CSV must contain 'Product name' and 'Quantity' columns.")
        else:
            if client == "Clean Eats":
                # Group and sum quantities
                grouped = df.groupby("Product name", as_index=False)["Quantity"].sum()

                # Identify extra items
                known_set = set(product_order)
                uploaded_set = set(grouped["Product name"])
                extras = list(uploaded_set - known_set)

                # Final ordered list = official + extras
                final_order = product_order + sorted(extras)

                # Build full zero-filled frame
                full_df = pd.DataFrame({"Product name": final_order})
                merged = pd.merge(full_df, grouped, on="Product name", how="left").fillna(0)
                merged["Quantity"] = merged["Quantity"].astype(int)

                # Display summary
                st.subheader("Summary Table")
                st.dataframe(merged, use_container_width=True)

                # Download as Excel
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

            elif client == "Made Active":
                st.warning("Made Active logic not yet implemented. This will handle bundle unpacking.")
    
    except Exception as e:
        st.error(f"Error reading file: {e}")
