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
            # 1️⃣ Ambil semua ITV (3 digit / TRAINING)
            # ===============================
            itv_columns = []

            for w in words:
                text = w["text"].strip()
                text_clean = re.sub(r'[^A-Z0-9]', '', text.upper())

                if re.fullmatch(r"\d{3}", text_clean) or "TRAINING" in text_clean:
                    itv_columns.append({
                        "x": w["x0"],
                        "value": "TRAINING" if "TRAINING" in text_clean else text_clean
                    })

            if not itv_columns:
                continue

            # Urutkan kolom dari kiri ke kanan
            itv_columns = sorted(itv_columns, key=lambda c: c["x"])

            # Ambil hanya 4 kolom pertama (biasanya memang 4 kolom tetap)
            # Ini supaya ITV header bawah tidak ikut dianggap kolom baru
            if len(itv_columns) > 4:
                itv_columns = itv_columns[:4]

            # ===============================
            # 2️⃣ Proses nomor 4 digit
            # ===============================
            i = 0
            while i < len(words):
                word = words[i]
                text = word["text"]

                match = re.match(r"(\d{4})(.*)", text)
                if match:
                    nomor = match.group(1)
                    sisa = match.group(2).strip()

                    nama_parts = []
                    if sisa:
                        nama_parts.append(sisa)

                    top = round(word["top"], 1)
                    j = i + 1

                    # Gabung nama dalam satu baris
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

                    # Tentukan kolom berdasarkan jarak paling dekat
                    x_person = word["x0"]

                    closest_column = min(
                        itv_columns,
                        key=lambda col: abs(col["x"] - x_person)
                    )

                    itv_value = closest_column["value"]
                    nama = " ".join(nama_parts).strip()

                    if nama:
                        data.append({
                            "ITV": itv_value,
                            "Nomor": nomor,
                            "Nama": nama
                        })

                    i = j
                else:
                    i += 1

    df = pd.DataFrame(data)

    if not df.empty:
        df = df.reset_index(drop=True)

    return df
