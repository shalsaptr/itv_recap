import pdfplumber
import pandas as pd
import re

def extract_itv_data(uploaded_file):
    data = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            current_itv = None

            for line in lines:
                # Deteksi ITV (misal: ITV 238)
                itv_match = re.search(r"ITV\s*(\d+)", line)
                if itv_match:
                    current_itv = itv_match.group(1)

                # Deteksi nomor dan nama (contoh: 7230 HARI SETYO CAHYANTO)
                name_match = re.match(r"(\d{3,5})\s+([A-Z\s\.]+)", line)
                if name_match and current_itv:
                    nomor = name_match.group(1)
                    nama = name_match.group(2).strip()

                    data.append({
                        "ITV": current_itv,
                        "Nomor": nomor,
                        "Nama": nama
                    })

    df = pd.DataFrame(data)
    return df
