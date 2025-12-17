# parsers/parse_monedas_extranjeras_raw.py

import json
import re
from pathlib import Path
import pdfplumber

BASE_DIR = Path(__file__).resolve().parents[1]
PDF_DIR = BASE_DIR / "outputs" / "pdfs"
OUT = BASE_DIR / "outputs" / "raw_monedas_2024.json"


def to_number(value: str | None):
    if not value:
        return None
    return float(
        value.replace(".", "").replace(",", ".").strip()
    )


def main():
    # Buscar cualquier PDF de moneda extranjera 2024
    pdfs = list(PDF_DIR.glob("*moneda*extranjera*2024*.pdf"))

    if not pdfs:
        print("⚠️  No se encontró PDF de Moneda Extranjera 2024. Se omite.")
        return

    pdf_path = pdfs[0]

    data = {
        "anio": 2024,
        "fuente": "ARCA",
        "origen": "PDF_MONEDA_EXTRANJERA",
        "valores": {},
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = text.splitlines()

            for line in lines:
                l = line.lower()

                if "billete" in l and "compra" in l:
                    m = re.search(r"([\d\.,]+)", line)
                    if m:
                        data["valores"]["billete_compra"] = m.group(1)

                if "billete" in l and "venta" in l:
                    m = re.search(r"([\d\.,]+)", line)
                    if m:
                        data["valores"]["billete_venta"] = m.group(1)

                if "divisa" in l and "compra" in l:
                    m = re.search(r"([\d\.,]+)", line)
                    if m:
                        data["valores"]["divisa_compra"] = m.group(1)

                if "divisa" in l and "venta" in l:
                    m = re.search(r"([\d\.,]+)", line)
                    if m:
                        data["valores"]["divisa_venta"] = m.group(1)

    OUT.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"✅ Monedas extranjeras RAW generado: {OUT}")


if __name__ == "__main__":
    main()
