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

            i = 0
            while i < len(words):
                word = words[i]
                text = word["text"].strip()
                x = word["x0"]
                top = round(word["top"], 1)

                # ==================================
                # 1️⃣ DETEKSI ITV ANGKA (3 digit)
                # ==================================
                if re.fullmatch(r"\d{3}", text):
                    current_itv_by_column[round(x, -1)] = text
                    i += 1
                    continue

                # ==================================
                # 2️⃣ DETEKSI ITV KHUSUS TRAINING
                # ==================================
                if text.upper() == "TRAINING":
                    current_itv_by_column[round(x, -1)] = "TRAINING"
                    i += 1
                    continue

                # ==================================
                # 3️⃣ DETEKSI NOMOR 4 DIGIT
                # ==================================
                match = re.match(r"(\d{4})(.*)", text)
                if match:
                    nomor = match.group(1)
                    sisa = match.group(2).strip()

                    nama_parts = []

                    if sisa:
                        nama_parts.append(sisa)

                    j = i + 1

                    while j < len(words):
                        next_word = words[j]
                        next_text = next_word["text"]
                        next_top = round(next_word["top"], 1)

                        # Stop kalau pindah baris
                        if abs(next_top - top) > 2:
                            break

                        # Stop kalau angka saja (kolom jumlah)
                        if re.fullmatch(r"\d+", next_text):
                            break

                        # Stop kalau nomor baru
                        if re.match(r"\d{4}", next_text):
                            break

                        nama_parts.append(next_text)
                        j += 1

                    if current_itv_by_column:
                        closest_col = min(
                            current_itv_by_column.keys(),
                            key=lambda col: abs(col - x)
                        )
                        itv = current_itv_by_column[closest_col]

                        nama = " ".join(nama_parts).strip()

                        if nama:
                            data.append({
                                "ITV": itv,
                                "Nomor": nomor,
                                "Nama": nama
                            })

                    i = j
                else:
                    i += 1

    df = pd.DataFrame(data)
    df = df.reset_index(drop=True)

    return df
