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

            # =========================
            # 1️⃣ Ambil ITV dari header atas saja
            # =========================
            header_itv = []

            for w in words:
                text = w["text"].strip().upper()

                # Ambil hanya ITV yang berada di bagian atas halaman
                if w["top"] < 200:  
                    if re.fullmatch(r"\d{3}", text) or text == "TRAINING":
                        header_itv.append((w["x0"], text))

            if not header_itv:
                continue

            # Urutkan berdasarkan posisi X (jadi kolom tetap)
            header_itv = sorted(header_itv, key=lambda x: x[0])

            # =========================
            # 2️⃣ Proses semua nomor 4 digit
            # =========================
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

                    # Tentukan kolom berdasarkan posisi X
                    x_person = w["x0"]

                    # Cari kolom header terdekat secara urutan
                    col_index = min(
                        range(len(header_itv)),
                        key=lambda idx: abs(header_itv[idx][0] - x_person)
                    )

                    itv_value = header_itv[col_index][1]
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
    df = df.reset_index(drop=True)

    return df
