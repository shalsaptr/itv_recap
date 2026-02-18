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

            # Kelompokkan berdasarkan baris (posisi vertikal)
            lines = {}
            for word in words:
                top = round(word["top"], 0)
                lines.setdefault(top, []).append(word)

            sorted_lines = sorted(lines.items(), key=lambda x: x[0])

            current_itv = []

            for _, line_words in sorted_lines:
                texts = [w["text"] for w in sorted(line_words, key=lambda x: x["x0"])]

                # =====================
                # DETEKSI ITV (3 digit saja)
                # =====================
                itv_candidates = [t for t in texts if re.fullmatch(r"\d{3}", t)]

                if len(itv_candidates) >= 1:
                    current_itv = itv_candidates
                    continue

                # =====================
                # DETEKSI NOMOR 4 digit
                # =====================
                row_text = " ".join(texts)
                matches = re.findall(r"(\d{4})\s+([A-Z][A-Z\s\.]+)", row_text)

                if matches and current_itv:
                    for idx, match in enumerate(matches):
                        nomor = match[0]
                        nama = match[1].strip()

                        # Cocokkan dengan ITV sesuai urutan
                        if idx < len(current_itv):
                            itv = current_itv[idx]
                        else:
                            itv = current_itv[0]

                        data.append({
                            "ITV": itv,
                            "Nomor": nomor,
                            "Nama": nama
                        })

    return pd.DataFrame(data)
