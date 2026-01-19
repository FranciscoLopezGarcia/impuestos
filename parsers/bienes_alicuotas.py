import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT = RAW_DIR / "raw_bienes_alicuotas_all.json"

URL = "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/conceptos-basicos/alicuotas.asp"
HEADERS = {"User-Agent": "Impuestos-Explorer"}

def parse():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table")

    data = {
        "fuente": "ARCA",
        "tablas": []
    }

    for idx, table in enumerate(tables):
        # texto cercano (contexto humano)
        context = table.find_previous(text=True)
        context_text = context.strip() if context else ""

        rows = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)

        data["tablas"].append({
            "index": idx,
            "contexto": context_text,
            "rows": rows
        })

    OUT.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"OK → {OUT} (tablas: {len(data['tablas'])})")

if __name__ == "__main__":
    parse()
