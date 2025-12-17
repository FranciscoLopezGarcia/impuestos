# parsers/parse_escalas_art94_raw_2024.py

import json
import re
from pathlib import Path

import pdfplumber

BASE_DIR = Path(__file__).resolve().parents[1]
PDF_DIR = BASE_DIR / "outputs" / "pdfs"
OUT = BASE_DIR / "outputs" / "raw_escalas_2024.json"


def main():
    pdfs = list(PDF_DIR.glob("*art-94*2024*.pdf"))

    if not pdfs:
        raise RuntimeError(
            "No se encontró PDF Art. 94 2024 en outputs/pdfs"
        )

    pdf_path = pdfs[0]

    result = {
        "anio": None,
        "fuente": "ARCA",
        "origen": "PDF_ART_94",
        "rows": [],
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""

            # Inferir año
            if result["anio"] is None:
                m = re.search(r"20\d{2}", text)
                if m:
                    result["anio"] = int(m.group(0))

            lines = text.splitlines()

            for line in lines:
                # Buscar líneas con números de escala
                nums = re.findall(r"[\d\.,]+", line)

                if len(nums) >= 5:
                    try:
                        desde = nums[0]
                        hasta = nums[1]
                        monto_fijo = nums[2]
                        porcentaje = nums[3]
                        excedente = nums[4]

                        result["rows"].append({
                            "desde": desde,
                            "hasta": hasta,
                            "monto_fijo": monto_fijo,
                            "porcentaje": porcentaje,
                            "excedente_desde": excedente,
                        })
                    except Exception:
                        continue

    OUT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"✅ Escalas Art. 94 RAW generado: {OUT}")


if __name__ == "__main__":
    main()
