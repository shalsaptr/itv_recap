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

            # Tentukan titik tengah halaman
            page_width = page.width
            midpoint = page_width / 2

            current_itv_left = None
            current_itv_right = None

            for i, word in enumerate(words):
                text = word["text"]
                x_position = word["x0"]

                # =====================
                # DETEKSI ITV
                # =====================
                if text.upper() == "ITV":
                    if i + 1 < len(words):
                        next_word = words[i + 1]["text"]

                        if re.match(r"\d{3}", next_word):

                            if x_position < midpoint:
                                current_itv_left = next_word
                            else:
                                current_itv_right = next_word

                    continue

                # =====================
                # DETEKSI NOMOR + NAMA GABUNG
                # =====================
                match = re.match(r"(\d{4})([A-Z\.]+)", text)

                if match:
                    nomor = match.group(1)
                    nama_awal = match.group(2)

                    # Ambil kata lanjutan nama
                    nama_lengkap = nama_awal

                    for j in range(i+1, min(i+5, len(words))):
                        next_text = words[j]["text"]

                        if re.match(r"[A-Z\.]+", next_text):
                            nama_lengkap += " " + next_text
                        else:
                            break

                    # Tentukan ITV berdasarkan posisi kiri/kanan
                    if x_position < midpoint:
                        current_itv = current_itv_left
                    else:
                        current_itv = current_itv_right

                    if current_itv:
                        data.append({
                            "ITV": current_itv,
                            "Nomor": nomor,
                            "Nama": nama_lengkap.strip()
                        })

    return pd.DataFrame(data)
