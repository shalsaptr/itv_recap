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

            current_itv_left = None
            current_itv_right = None

            for line in lines:

                # ==========================
                # DETEKSI BARIS ITV (misal: 238 255)
                # ==========================
                itv_line = re.findall(r"\b\d{3}\b", line)

                if len(itv_line) >= 2:
                    current_itv_left = itv_line[0]
                    current_itv_right = itv_line[1]
                    continue

                # ==========================
                # DETEKSI NOMOR + NAMA
                # ==========================
                matches = re.findall(r"(\d{4})\s+([A-Z\s\.]+)", line)

                if matches:
                    for idx, match in enumerate(matches):
                        nomor = match[0]
                        nama = match[1].strip()

                        # Tentukan kiri atau kanan berdasarkan urutan
                        if idx == 0:
                            current_itv = current_itv_left
                        else:
                            current_itv = current_itv_right

                        if current_itv:
                            data.append({
                                "ITV": current_itv,
                                "Nomor": nomor,
                                "Nama": nama
                            })

    return pd.DataFrame(data)
