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

            # Urutkan berdasarkan posisi vertikal dulu
            words = sorted(words, key=lambda w: (w["top"], w["x0"]))

            current_itv = None
            last_top = None

            for word in words:
                text = word["text"]
                top = round(word["top"], 1)

                # Jika pindah baris cukup jauh → reset ITV detection
                if last_top and abs(top - last_top) > 15:
                    pass

                last_top = top

                # =============================
                # DETEKSI ITV (3 digit saja)
                # =============================
                if re.fullmatch(r"\d{3}", text):
                    current_itv = text
                    continue

                # =============================
                # DETEKSI NOMOR + NAMA
                # =============================
                match = re.match(r"(\d{4})([A-Z\.]*)", text)

                if match and current_itv:
                    nomor = match.group(1)
                    nama = match.group(2)

                    data.append({
                        "ITV": current_itv,
                        "Nomor": nomor,
                        "Nama": nama
                    })

    df = pd.DataFrame(data)

    # Bersihkan data kosong
    df = df[df["Nama"] != ""]
    df = df.reset_index(drop=True)

    return df
