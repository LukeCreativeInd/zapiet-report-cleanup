import pandas as pd
import io
import streamlit as st

# Bundle contents
bundle_map = {
    "High Protein Pack": {
        "Chicken Fajita Bowl": 2,
        "Thai Green Chicken Curry": 2,
        "Naked Chicken Parma": 2,
        "Beef Burrito Bowl": 2,
        "Spaghetti Bolognese": 2,
        "Mongolian Beef": 2,
    },
    "30 Pack": {
        "Chicken Fajita Bowl": 4,
        "Mongolian Beef": 4,
        "Chicken with Vegetables": 3,
        "Thai Green Chicken Curry": 4,
        "Naked Chicken Parma": 4,
        "Butter Chicken": 3,
        "Spaghetti Bolognese": 4,
        "Beef Burrito Bowl": 4,
    },
    "20 Pack": {
        "Chicken Fajita Bowl": 2,
        "Mongolian Beef": 3,
        "Chicken with Vegetables": 3,
        "Thai Green Chicken Curry": 2,
        "Naked Chicken Parma": 3,
        "Butter Chicken": 2,
        "Spaghetti Bolognese": 2,
        "Beef Burrito Bowl": 3,
    },
    "10 Pack": {
        "Chicken Fajita Bowl": 1,
        "Mongolian Beef": 2,
        "Chicken with Vegetables": 1,
        "Thai Green Chicken Curry": 1,
        "Naked Chicken Parma": 1,
        "Butter Chicken": 2,
        "Spaghetti Bolognese": 1,
        "Beef Burrito Bowl": 1,
    }
}

# Name normalization mapping
name_map = {
    "Chicken with Broccoli & Beans": "Chicken with Vegetables",
    "Butter Chicken with Basmati Rice": "Butter Chicken",
    "Baked Chicken Breast": "Steak On Its Own",
    "Porterhouse Steak": "Chicken On Its Own"
}

def run_made_active_flow(df, product_order):
    # Apply name mapping
    df["Product name"] = df["Product name"].replace(name_map)

    # Extract bundles
    bundle_rows = df[df["Product name"].isin(bundle_map.keys())]
    unpacked_rows = []

    for _, row in bundle_rows.iterrows():
        bundle_name = row["Product name"]
        bundle_qty = row["Quantity"]

        if bundle_name in bundle_map:
            for item_name, item_qty in bundle_map[bundle_name].items():
                unpacked_rows.append({
                    "Product name": item_name,
                    "Quantity": item_qty * bundle_qty
                })

    # Remove bundles from original DataFrame
    df = df[~df["Product name"].isin(bundle_map.keys())]

    # Add unpacked bundle items
    if unpacked_rows:
        df = pd.concat([df, pd.DataFrame(unpacked_rows)], ignore_index=True)

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
