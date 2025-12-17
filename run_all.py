# run_all.py
import argparse
import json
import subprocess
import sys
from pathlib import Path

from arca.pipeline import collect_sources
from arca.fetcher import fetch_pdfs
from normalizers.normalize_all import normalize_all
from parametros_arca import update_excel

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
EXCEL_PATH = Path(r"C:\Users\franl\Desktop\impuestos\CH - Anuales 2024.xlsx")


def run(year: int):
    print(f"\n▶ PROCESO ANUAL {year}\n")

    # 1️⃣ Crawl + clasificar
    sources = collect_sources(year)

    # 2️⃣ Descargar PDFs
    fetch_pdfs(sources)


    # 3️⃣ Parsers (orden explícito)
    subprocess.run([sys.executable, "parsers/parse_bp_determinativa_html_raw.py"], check=True)
    subprocess.run([sys.executable, "parsers/parse_bienes_alicuotas_html_raw.py"], check=True)
    subprocess.run([sys.executable, "parsers/parse_monedas_extranjeras_raw.py"], check=True)
    subprocess.run([sys.executable, "parsers/parse_art30_raw_2024.py"], check=True)
    subprocess.run([sys.executable, "parsers/parse_escalas_art94_raw_2024.py"], check=True)


    # 4️⃣ Normalizar
    parametros = normalize_all(year)

    year_dir = OUTPUTS_DIR / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)

    json_out = year_dir / "parametros_arca.json"
    json_out.write_text(
        json.dumps(parametros, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # 5️⃣ Excel
    update_excel(json_out, EXCEL_PATH)

    print("\n✅ PROCESO COMPLETO\n")


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()
    run(args.year)


if __name__ == "__main__":
    cli()
