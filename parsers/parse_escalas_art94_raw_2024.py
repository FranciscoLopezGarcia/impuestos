# parse_escalas_art94_raw.py
import pdfplumber
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

PDF = BASE_DIR / "outputs" / "pdfs" / "Tabla-Art-94-LIG-liquidacion-anual-y-final-2025.pdf"
OUT = Path(__file__).resolve().parents[1] / "outputs" / "raw_escalas_2024.json"

def parse():
    rows = []

    with pdfplumber.open(PDF) as pdf:
        for table in pdf.pages[0].extract_tables():
            for row in table:
                if not row or "Ganancia" in row[0]:
                    continue
                rows.append({
                    "desde": row[0],
                    "hasta": row[1],
                    "monto_fijo": row[2],
                    "porcentaje": row[3],
                    "excedente_desde": row[4],
                })

    OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    parse()
