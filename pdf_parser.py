import pdfplumber
import pandas as pd
import re

def extract_itv_data(uploaded_file):
    data = []

    with pdfplumber.open(uploaded_file) as pdf:
        full_text = ""

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += "\n" + text

    # Bersihkan kasus nama nempel nomor
    full_text = re.sub(r"([A-Z])(\d{4})", r"\1 \2", full_text)

    lines = full_text.split("\n")

    current_itvs = []

    for line in lines:
        line = line.strip()

        # ==========================
        # 1️⃣ DETEKSI BARIS ITV (3 digit banyak)
        # ==========================
        itv_matches = re.findall(r"\b\d{3}\b", line)
        if len(itv_matches) >= 1:
            current_itvs = itv_matches
            continue

        # ==========================
        # 2️⃣ DETEKSI NOMOR + NAMA
        # ==========================
        match = re.match(r"(\d{4})\s+(.+)", line)
        if match and current_itvs:
            nomor = match.group(1)
            nama = match.group(2).strip()

            # Assign ke ITV secara urut
            for itv in current_itvs:
                data.append({
                    "ITV": itv,
                    "Nomor": nomor,
                    "Nama": nama
                })

    df = pd.DataFrame(data)
    return df
