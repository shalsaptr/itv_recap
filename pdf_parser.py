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

            # Urutkan berdasarkan posisi (atas ke bawah, kiri ke kanan)
            words = sorted(words, key=lambda w: (w["top"], w["x0"]))

            current_itv_by_column = {}

            i = 0
            while i < len(words):
                word = words[i]
                text = word["text"]
                x = word["x0"]

                # ============================
                # DETEKSI ITV (angka 3 digit ATAU huruf seperti TRAINING)
                # ============================
                if re.fullmatch(r"\d{3}", text) or text.isalpha():
                    current_itv_by_column[round(x, -1)] = text
                    i += 1
                    continue

                # ============================
                # DETEKSI NOMOR 4 DIGIT
                # ============================
                if re.fullmatch(r"\d{4}", text):
                    nomor = text
                    nama_parts = []

                    j = i + 1

                    # Ambil semua kata kapital setelah nomor sebagai nama
                    while j < len(words):
                        next_word = words[j]
                        next_text = next_word["text"]

                        # Stop jika ketemu nomor lagi atau ITV lagi
                        if re.fullmatch(r"\d{4}", next_text) or re.fullmatch(r"\d{3}", next_text):
                            break

                        if re.match(r"[A-Z\.]+", next_text):
                            nama_parts.append(next_text)
                            j += 1
                        else:
                            break

                    # Cari ITV berdasarkan kolom terdekat
                    closest_col = min(
                        current_itv_by_column.keys(),
                        key=lambda col: abs(col - x),
                        default=None
                    )

                    if closest_col:
                        itv = current_itv_by_column[closest_col]
                        nama = " ".join(nama_parts)

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
