import streamlit as st
import pandas as pd

st.title("Meal Production Report Summary")

# Group selection
group = st.selectbox("Select Business Group", ["Clean Eats Australia", "Made Active", "Elite Meals"])

# File uploader
uploaded_file = st.file_uploader("Upload Zapiet Report (CSV or Excel)", type=["csv", "xlsx"])

generate = st.button("Generate Report")

if generate and uploaded_file:
    # Read uploaded file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()
    if "product name" in df.columns:
        product_col = "product name"
    elif "Product name" in df.columns:
        product_col = "Product name"
    else:
        st.error("Cannot find 'Product name' column.")
        st.stop()

    # Standardize the column name
    df.rename(columns={product_col: "Product"}, inplace=True)

    # Load mapping based on group
    if group == "Clean Eats Australia":
        mapping = {
            "Butter Chicken with Basmati Rice": "Butter Chicken",
            "Chicken with Broccoli & Beans": "Chicken with Vegetables",
            "Baked Chicken Breast": "Steak On Its Own",
            "Porterhouse Steak": "Chicken On Its Own"
        }
    elif group == "Made Active":
        mapping = {
            "Butter Chicken with Basmati Rice": "Butter Chicken",
            "Chicken with Broccoli & Beans": "Chicken with Vegetables",
            "Baked Chicken Breast": "Steak On Its Own",
            "Porterhouse Steak": "Chicken On Its Own"
        }
    elif group == "Elite Meals":
        elite_mapping = pd.read_excel("Elite Meals Mapping.xlsx")
        mapping = dict(zip(elite_mapping["Report Mapping Name"], elite_mapping["Elite Meals Meals"]))
    else:
        mapping = {}

    # Map and clean data
    df["Standardized Meal"] = df["Product"].replace(mapping)
    df["Standardized Meal"] = df["Standardized Meal"].fillna(df["Product"])  # Keep original if no match

    # Group and sum
    if "quantity" not in df.columns:
        st.error("Missing 'Quantity' column in uploaded file.")
        st.stop()

    summary = df.groupby("Standardized Meal")["quantity"].sum().reset_index()
    summary.columns = ["Meal", "Total Quantity"]
    summary = summary.sort_values(by="Total Quantity", ascending=False)

    # Display
    st.subheader("Meal Summary Report")
    st.dataframe(summary, use_container_width=True)

    # Download
    csv = summary.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "meal_summary.csv", "text/csv")
