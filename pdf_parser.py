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

            # Urutkan berdasarkan posisi
            words = sorted(words, key=lambda w: (w["top"], w["x0"]))

            current_itv_by_column = {}

            i = 0
            while i < len(words):
                word = words[i]
                text = word["text"].strip()
                x = word["x0"]

                # ======================
                # DETEKSI ITV (3 digit atau TRAINING)
                # ======================
                text_clean = re.sub(r'[^A-Z0-9]', '', text.upper())

                if re.fullmatch(r"\d{3}", text_clean):
                    current_itv_by_column[round(x, -1)] = text_clean
                    i += 1
                    continue

                elif "TRAINING" in text_clean:
                    current_itv_by_column[round(x, -1)] = "TRAINING"
                    i += 1
                    continue

                # ======================
                # DETEKSI NOMOR 4 DIGIT
                # ======================
                match = re.match(r"(\d{4})(.*)", text)
                if match:
                    nomor = match.group(1)
                    sisa = match.group(2).strip()

                    nama_parts = []
                    if sisa:
                        nama_parts.append(sisa)

                    top = round(word["top"], 1)
                    j = i + 1

                    # Gabungkan nama dalam baris yang sama
                    while j < len(words):
                        next_word = words[j]
                        next_text = next_word["text"]
                        next_top = round(next_word["top"], 1)

                        # Berhenti kalau beda baris
                        if abs(next_top - top) > 3:
                            break

                        # Stop kalau ketemu angka lagi
                        if re.fullmatch(r"\d+", next_text):
                            break

                        if re.match(r"\d{4}", next_text):
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

                    i = j
                else:
                    i += 1

    df = pd.DataFrame(data)

    if not df.empty:
        df = df.reset_index(drop=True)

    return df
