# parsers/parse_art30_raw_2024.py

import json
import re
from pathlib import Path

import pdfplumber

BASE_DIR = Path(__file__).resolve().parents[1]
PDF_DIR = BASE_DIR / "outputs" / "pdfs"
OUT = BASE_DIR / "outputs" / "raw_art30_2024.json"


def to_number(value: str | None):
    if not value:
        return None
    return float(
        value.replace(".", "").replace(",", ".").strip()
    )


def main():
    pdfs = list(PDF_DIR.glob("*art-30*2024*.pdf"))

    if not pdfs:
        raise RuntimeError(
            "No se encontró PDF Art. 30 2024 en outputs/pdfs"
        )

    pdf_path = pdfs[0]

    data = {
        "anio": None,
        "fuente": "ARCA",
        "origen": "PDF_ART_30",
        "items": {},
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""

            # Intentar inferir año
            if data["anio"] is None:
                m = re.search(r"20\d{2}", text)
                if m:
                    data["anio"] = int(m.group(0))

            lines = text.splitlines()

            for line in lines:
                l = line.lower()

                if "ganancia no imponible" in l:
                    m = re.search(r"([\d\.,]+)", line)
                    if m:
                        data["items"]["ganancia_no_imponible"] = m.group(1)

                if "cónyuge" in l or "conyuge" in l:
                    m = re.search(r"([\d\.,]+)", line)
                    if m:
                        data["items"]["cargas_conyuge"] = m.group(1)

                if "hijo" in l and "incapacitado" not in l:
                    m = re.search(r"([\d\.,]+)", line)
                    if m:
                        data["items"]["cargas_hijo"] = m.group(1)

                if "hijo incapacitado" in l:
                    m = re.search(r"([\d\.,]+)", line)
                    if m:
                        data["items"]["cargas_hijo_incap"] = m.group(1)

                if "deducción especial" in l or "deduccion especial" in l:
                    m = re.search(r"([\d\.,]+)", line)
                    if m:
                        data["items"]["deduccion_especial"] = m.group(1)

    OUT.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"✅ Art. 30 RAW generado: {OUT}")


if __name__ == "__main__":
    main()
