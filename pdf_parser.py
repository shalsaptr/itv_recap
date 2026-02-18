import pdfplumber
import pandas as pd
import re

def extract_itv_data(uploaded_file):
    data = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            words = page.extract_words()

            # Urutkan berdasarkan posisi vertikal lalu horizontal
            words = sorted(words, key=lambda w: (w["top"], w["x0"]))

            current_itv = None

            for i, word in enumerate(words):
                text = word["text"]

                # Deteksi ITV
                if text.upper() == "ITV":
                    # Angka setelah ITV adalah nomor ITV
                    if i + 1 < len(words):
                        next_word = words[i + 1]["text"]
                        if re.match(r"\d{3}", next_word):
                            current_itv = next_word
                    continue

                # Deteksi nomor karyawan (4 digit)
                if re.match(r"\d{4}", text):
                    nomor = text
                    nama = ""

                    # Ambil beberapa kata setelahnya sebagai nama
                    for j in range(i+1, min(i+6, len(words))):
                        next_text = words[j]["text"]

                        if re.match(r"[A-Z\.]+", next_text):
                            nama += next_text + " "
                        else:
                            break

                    if current_itv and nama:
                        data.append({
                            "ITV": current_itv,
                            "Nomor": nomor,
                            "Nama": nama.strip()
                        })

    df = pd.DataFrame(data)
    return df
