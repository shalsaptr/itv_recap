import pdfplumber
import pandas as pd
import re

def extract_itv_data(uploaded_file):
    data = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=3, y_tolerance=3)

            if not words:
                continue

            words = sorted(words, key=lambda w: (w["top"], w["x0"]))

            # ===============================
            # 1️⃣ Ambil semua ITV dulu
            # ===============================
            itv_columns = {}

            for w in words:
                text = w["text"].strip().upper()

                if re.fullmatch(r"\d{3}", text) or text == "TRAINING":
                    itv_columns[w["x0"]] = text

            if not itv_columns:
                continue

            # ===============================
            # 2️⃣ Ambil semua orang
            # ===============================
            i = 0
            while i < len(words):
                w = words[i]
                text = w["text"]

                match = re.match(r"(\d{4})(.*)", text)
                if match:
                    nomor = match.group(1)
                    sisa = match.group(2).strip()

                    nama_parts = []
                    if sisa:
                        nama_parts.append(sisa)

                    top = round(w["top"], 1)
                    j = i + 1

                    while j < len(words):
                        next_word = words[j]
                        next_text = next_word["text"]
                        next_top = round(next_word["top"], 1)

                        if abs(next_top - top) > 3:
                            break

                        if re.fullmatch(r"\d+", next_text):
                            break

                        if re.match(r"\d{4}", next_text):
                            break

                        nama_parts.append(next_text)
                        j += 1

                    # Cari ITV kolom terdekat
                    closest_itv = min(
                        itv_columns.items(),
                        key=lambda item: abs(item[0] - w["x0"])
                    )[1]

                    nama = " ".join(nama_parts).strip()

                    if nama:
                        data.append({
                            "ITV": closest_itv,
                            "Nomor": nomor,
                            "Nama": nama
                        })

                    i = j
                else:
                    i += 1

    df = pd.DataFrame(data)
    df = df.reset_index(drop=True)

    return df
