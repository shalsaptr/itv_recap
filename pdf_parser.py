import pdfplumber
import pandas as pd
import re
from collections import defaultdict

def extract_itv_data(uploaded_file):
    data = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=3, y_tolerance=3)

            if not words:
                continue

            # Kelompokkan berdasarkan baris (top)
            lines = defaultdict(list)
            for w in words:
                line_key = round(w["top"], 1)
                lines[line_key].append(w)

            # Urutkan baris dari atas ke bawah
            for top in sorted(lines.keys()):
                line_words = sorted(lines[top], key=lambda w: w["x0"])

                # ============================
                # 1️⃣ Ambil semua ITV dalam baris
                # ============================
                itv_positions = []

                for w in line_words:
                    text = w["text"].strip().upper()

                    if re.fullmatch(r"\d{3}", text):
                        itv_positions.append((w["x0"], text))

                    elif "TRAINING" in text:
                        itv_positions.append((w["x0"], "TRAINING"))

                # ============================
                # 2️⃣ Cari nomor 4 digit
                # ============================
                i = 0
                while i < len(line_words):
                    word = line_words[i]
                    text = word["text"]

                    match = re.match(r"(\d{4})(.*)", text)
                    if match:
                        nomor = match.group(1)
                        sisa = match.group(2).strip()

                        nama_parts = []
                        if sisa:
                            nama_parts.append(sisa)

                        j = i + 1
                        while j < len(line_words):
                            next_text = line_words[j]["text"]

                            if re.fullmatch(r"\d+", next_text):
                                break

                            if re.match(r"\d{4}", next_text):
                                break

                            nama_parts.append(next_text)
                            j += 1

                        # Cari ITV terdekat berdasarkan posisi X
                        if itv_positions:
                            x_person = word["x0"]

                            closest_itv = min(
                                itv_positions,
                                key=lambda itv: abs(itv[0] - x_person)
                            )

                            itv_value = closest_itv[1]
                            nama = " ".join(nama_parts).strip()

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
