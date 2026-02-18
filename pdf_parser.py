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
            # 1️⃣ Deteksi semua ITV header
            # ===============================
            itv_map = {}

            for w in words:
                text = w["text"].strip()
                text_clean = re.sub(r'[^A-Z0-9]', '', text.upper())

                # Ambil ITV hanya di bagian atas halaman
                if w["top"] < 250:
                    if re.fullmatch(r"\d{3}", text_clean):
                        itv_map[w["x0"]] = text_clean
                    elif "TRAINING" in text_clean:
                        itv_map[w["x0"]] = "TRAINING"

            if not itv_map:
                continue

            # Urutkan kolom berdasarkan X
            sorted_columns = sorted(itv_map.items(), key=lambda x: x[0])
            column_x_positions = [col[0] for col in sorted_columns]
            column_values = [col[1] for col in sorted_columns]

            # ===============================
            # 2️⃣ Proses nomor & nama
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

                    while j < len(words):
                        next_word = words[j]
                        next_text = next_word["text"]
                        next_top = round(next_word["top"], 1)

                        if abs(next_top - top) > 3:
                            break

                        if re.match(r"\d{4}", next_text):
                            break

                        if re.fullmatch(r"\d+", next_text):
                            break

                        nama_parts.append(next_text)
                        j += 1

                    # Tentukan kolom berdasarkan posisi X terdekat
                    x_person = word["x0"]

                    closest_index = min(
                        range(len(column_x_positions)),
                        key=lambda idx: abs(column_x_positions[idx] - x_person)
                    )

                    itv_value = column_values[closest_index]
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
