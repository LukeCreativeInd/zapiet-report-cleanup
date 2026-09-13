import io
import pandas as pd
import streamlit as st
from product_mapping import PRODUCT_ORDER, BUNDLE_REASON, clean_products


def run_summary_flow(df, product_order, client):
    if list(product_order) != PRODUCT_ORDER:
        raise ValueError('The cleanup menu does not match the production report menu.')
    try:
        merged, excluded = clean_products(df, client)
    except ValueError as error:
        st.error(str(error))
        return
    if not excluded.empty:
        review = excluded[excluded['Reason'] != BUNDLE_REASON]
        bundles = excluded[excluded['Reason'] == BUNDLE_REASON]
        if not review.empty:
            st.warning('These products are excluded from the production file. Review the names, quantities and reasons below, including any retired or inactive meals.')
            st.dataframe(review, width='stretch', hide_index=True)
        if not bundles.empty:
            st.info('Bundle and membership titles are excluded. Individual meal lines in the uploaded file are counted separately.')
            st.dataframe(bundles, width='stretch', hide_index=True)
    st.subheader('Summary Table')
    st.dataframe(merged, width='stretch', hide_index=True)
    st.caption(f"Total meals included: {int(merged['Quantity'].sum()):,}")
    filename = client.lower().replace(' ', '_') + '_summary'
    st.download_button('Download Summary as CSV', merged.to_csv(index=False).encode('utf-8-sig'),
                       file_name=filename+'.csv', mime='text/csv')
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        merged.to_excel(writer, index=False, sheet_name='Summary')
    st.download_button('Download Summary as Excel', buffer.getvalue(),
                       file_name=filename+'.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return merged


def run_clean_eats_flow(df, product_order):
    return run_summary_flow(df, product_order, 'Clean Eats')
