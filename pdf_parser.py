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

            # Kelompokkan berdasarkan baris (posisi Y)
            lines = {}
            for word in words:
                top = round(word["top"], 0)
                lines.setdefault(top, []).append(word)

            sorted_lines = sorted(lines.items(), key=lambda x: x[0])

            current_itvs = []

            for _, line_words in sorted_lines:
                # Urutkan kiri ke kanan
                line_words = sorted(line_words, key=lambda w: w["x0"])
                texts = [w["text"] for w in line_words]

                # =============================
                # DETEKSI BARIS ITV (3 digit)
                # =============================
                itv_candidates = [t for t in texts if re.fullmatch(r"\d{3}", t)]

                if len(itv_candidates) >= 1:
                    current_itvs = itv_candidates
                    continue

                # =============================
                # DETEKSI SEMUA NOMOR 4 DIGIT DI BARIS
                # =============================
                row_text = " ".join(texts)
                matches = re.findall(r"(\d{4})\s+([A-Z][A-Z\s\.]+)", row_text)

                if matches and current_itvs:
                    for idx, (nomor, nama) in enumerate(matches):

                        if idx < len(current_itvs):
                            itv = current_itvs[idx]
                        else:
                            itv = current_itvs[-1]

                        data.append({
                            "ITV": itv,
                            "Nomor": nomor,
                            "Nama": nama.strip()
                        })

    return pd.DataFrame(data)
