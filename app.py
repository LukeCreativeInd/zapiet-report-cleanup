import streamlit as st
import pandas as pd
from clean_eats import run_clean_eats_flow
from made_active import run_made_active_flow
from product_mapping import PRODUCT_ORDER, prepare_input

st.set_page_config(page_title='Product Quantity Summary', layout='centered')
selected_client = st.radio('Select Client', ['Clean Eats', 'Made Active'], horizontal=True)


def read_upload(upload):
    try:
        frame = pd.read_csv(upload) if upload.name.lower().endswith('.csv') else pd.read_excel(upload)
        return prepare_input(frame)
    except Exception as error:
        st.error(f'{upload.name}: {error}')
        return None


if selected_client == 'Clean Eats':
    st.markdown('**Upload one or two Zapiet Production Report files. The second file is optional.**')
    first = st.file_uploader('Clean Eats – File 1 (CSV or Excel)', type=['csv','xlsx'], key='ce1')
    second = st.file_uploader('Clean Eats – File 2 (Optional)', type=['csv','xlsx'], key='ce2')
    uploads = [f for f in (first,second) if f is not None]
    flow = run_clean_eats_flow
else:
    first = st.file_uploader('Upload Zapiet Production Report (CSV or Excel)', type=['csv','xlsx'], key='ma')
    uploads = [first] if first is not None else []
    flow = run_made_active_flow

if st.button('Generate Report'):
    if not uploads:
        st.error('Please upload at least one file to continue.')
    else:
        frames = [read_upload(f) for f in uploads]
        # Do not offer a partial order if either selected file failed validation.
        if all(frame is not None for frame in frames):
            combined = pd.concat(frames, ignore_index=True)
            st.subheader('Raw Data Preview')
            st.dataframe(combined.head(), width='stretch')
            flow(combined, PRODUCT_ORDER)
