import streamlit as st
import pandas as pd
from pdf_parser import extract_itv_data
from io import BytesIO

st.set_page_config(page_title="PDF ITV Rekap", layout="wide")

st.title("📄 PDF to Excel - Rekap ITV")

uploaded_file = st.file_uploader("Upload File PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner("Membaca PDF..."):
        df = extract_itv_data(uploaded_file)

    if not df.empty:
        st.success("Data berhasil dibaca!")

        st.dataframe(df)

        # Convert to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Rekap ITV")

        output.seek(0)

        st.download_button(
            label="📥 Download Excel",
            data=output,
            file_name="rekap_itv.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Tidak ditemukan data ITV dalam PDF.")
