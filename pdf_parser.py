import pdfplumber
import pandas as pd
import re

def extract_itv_data(uploaded_file):
    data = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            words = page.extract_words()

            if not words:
                continue

            words = sorted(words, key=lambda w: (w["top"], w["x0"]))

            current_itv_by_column = {}

            for word in words:
                text = word["text"]
                x = word["x0"]

                # =========================
                # DETEKSI ITV (3 digit saja)
                # =========================
                if re.fullmatch(r"\d{3}", text):
                    current_itv_by_column[round(x, -1)] = text
                    continue

                # =========================
                # DETEKSI NOMOR + NAMA GABUNG
                # =========================
                match = re.match(r"(\d{4})(.*)", text)

                if match:
                    nomor = match.group(1)
                    sisa = match.group(2).strip()

                    # Cari ITV berdasarkan kolom terdekat
                    if current_itv_by_column:
                        closest_col = min(
                            current_itv_by_column.keys(),
                            key=lambda col: abs(col - x)
                        )
                        itv = current_itv_by_column[closest_col]

                        # Nama bisa jadi di word yang sama atau kosong
                        nama = sisa

                        data.append({
                            "ITV": itv,
                            "Nomor": nomor,
                            "Nama": nama
                        })

    df = pd.DataFrame(data)
    df = df[df["Nomor"].notna()]
    df = df.reset_index(drop=True)

    return df
