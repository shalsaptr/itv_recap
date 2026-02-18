import pdfplumber
import pandas as pd
import re

def extract_itv_data(pdf_path):
    data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            words = page.extract_words(x_tolerance=2, y_tolerance=2)
            words = sorted(words, key=lambda w: (w["top"], w["x0"]))

            # Kelompokkan berdasarkan baris (top mirip)
            rows = {}
            for w in words:
                top_key = round(w["top"] / 5) * 5
                rows.setdefault(top_key, []).append(w)

            current_itvs = []

            for row in rows.values():
                row = sorted(row, key=lambda w: w["x0"])
                texts = [w["text"] for w in row]

                # ==============================
                # 1️⃣ DETEKSI BARIS ITV (3 angka)
                # ==============================
                itv_matches = [t for t in texts if re.fullmatch(r"\d{3}", t)]
                if len(itv_matches) >= 1:
                    current_itvs = itv_matches
                    continue

                # ==============================
                # 2️⃣ DETEKSI 3 KOLOM NOMOR + NAMA
                # ==============================
                combined = " ".join(texts)

                matches = re.findall(r"(\d{4})\s+([A-Z\.\'\- ]+)", combined)

                if matches and current_itvs:
                    for idx, match in enumerate(matches):
                        if idx < len(current_itvs):
                            data.append({
                                "ITV": current_itvs[idx],
                                "Nomor": match[0],
                                "Nama": match[1].strip()
                            })

    df = pd.DataFrame(data)
    return df
