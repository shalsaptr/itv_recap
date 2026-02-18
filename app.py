import streamlit as st
import pandas as pd
from pdf_parser import extract_itv_data
from io import BytesIO

st.title("PDF → Rekap ITV")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    df = extract_itv_data(uploaded_file)

    if not df.empty:
        st.success("Data berhasil dibaca")
        st.dataframe(df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        output.seek(0)

        st.download_button(
            label="Download Excel",
            data=output,
            file_name="rekap_itv.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Tidak ditemukan data ITV dalam PDF.")
