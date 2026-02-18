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

            # Urutkan berdasarkan posisi
            words = sorted(words, key=lambda w: (w["top"], w["x0"]))

            current_itv_by_column = {}

            for i, word in enumerate(words):
                text = word["text"]
                x = word["x0"]
                top = round(word["top"], 1)

                # ======================
                # DETEKSI ITV (3 digit)
                # ======================
                if re.fullmatch(r"\d{3}", text):
                    current_itv_by_column[round(x, -1)] = text
                    continue

                # ======================
                # DETEKSI NOMOR 4 DIGIT
                # ======================
                if re.fullmatch(r"\d{4}", text):
                    nomor = text
                    nama_parts = []

                    # Ambil semua kata setelahnya di baris yang sama
                    j = i + 1
                    while j < len(words):
                        next_word = words[j]
                        next_text = next_word["text"]
                        next_top = round(next_word["top"], 1)

                        # Stop kalau pindah baris
                        if abs(next_top - top) > 2:
                            break

                        # Stop kalau ketemu nomor lagi
                        if re.fullmatch(r"\d{4}", next_text):
                            break

                        nama_parts.append(next_text)
                        j += 1

                    # Cari ITV berdasarkan kolom terdekat
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

    df = pd.DataFrame(data)
    df = df.reset_index(drop=True)

    return df
