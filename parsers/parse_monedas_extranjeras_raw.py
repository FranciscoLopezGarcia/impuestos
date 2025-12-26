import json
import re
from pathlib import Path
import pdfplumber
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
FILES_DIR = Path(r"C:\Users\franl\Desktop\impuestos\files")
year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
PDF = FILES_DIR / f"Valuaciones-{year}-Moneda-Extranjera.pdf"
OUT = BASE_DIR / "outputs" / f"raw_monedas_{year}.json"


MONEY_RE = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2,6}")  # 1.029,000000 / 113.643,398800

def extract_two_numbers(row) -> tuple[str | None, str | None]:
    """
    Encuentra los dos primeros valores numéricos (comprador/vendedor)
    en cualquier posición de la fila.
    """
    nums = []
    for cell in row:
        if not cell:
            continue
        for m in MONEY_RE.findall(str(cell)):
            nums.append(m)
        if len(nums) >= 2:
            break
    if len(nums) >= 2:
        return nums[0], nums[1]
    return None, None

def parse_table(table, kind: str):
    out = []
    for row in table[1:]:
        if not row:
            continue
        desc = (row[0] or "").strip()
        if not desc:
            continue

        comprador, vendedor = extract_two_numbers(row)
        out.append({
            "descripcion": desc,
            "comprador": comprador,
            "vendedor": vendedor
        })
    return out

def parse():
    data = {
        "anio": 2024,
        "fuente": "ARCA",
        "divisas": [],
        "billetes": [],
    }

    with pdfplumber.open(PDF) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables() or []

        if len(tables) < 2:
            raise RuntimeError(f"Se esperaban 2 tablas (DIVISAS y BILLETES). Detectadas: {len(tables)}")

        # En este PDF salen como table[0]=DIVISAS y table[1]=BILLETES
        data["divisas"] = parse_table(tables[0], "divisas")
        data["billetes"] = parse_table(tables[1], "billetes")

    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK -> {OUT}")

if __name__ == "__main__":
    parse()
