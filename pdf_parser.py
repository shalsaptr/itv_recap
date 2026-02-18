import pdfplumber
import pandas as pd
import re

ALLOWED_TEXT_ITV = {"TRAINING"}

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
                text = word["text"]
                x = word["x0"]

                # =============================
                # DETEKSI ITV (3 digit saja)
                # =============================
                if re.fullmatch(r"\d{3}", text):
                    current_itv_by_column[round(x, -1)] = text
                    i += 1
                    continue

                # =============================
                # DETEKSI ITV KHUSUS TEXT (TRAINING)
                # =============================
                if text in ALLOWED_TEXT_ITV:
                    current_itv_by_column[round(x, -1)] = text
                    i += 1
                    continue

                # =============================
                # DETEKSI NOMOR 4 DIGIT
                # =============================
                if re.fullmatch(r"\d{4}", text):
                    nomor = text
                    nama_parts = []
                    j = i + 1

                    while j < len(words):
                        next_text = words[j]["text"]

                        if re.fullmatch(r"\d{4}", next_text) or re.fullmatch(r"\d{3}", next_text):
                            break

                        if re.match(r"[A-Z\.]+", next_text):
                            nama_parts.append(next_text)
                            j += 1
                        else:
                            break

                    if current_itv_by_column:
                        closest_col = min(
                            current_itv_by_column.keys(),
                            key=lambda col: abs(col - x)
                        )
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
