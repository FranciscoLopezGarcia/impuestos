import argparse
import json
from pathlib import Path

from normalizers.normalize_all import normalize_all
from parametros_arca import update_excel


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
EXCEL_PATH = Path(r"C:\Users\franl\Desktop\impuestos\CH - Anuales 2024.xlsx")


def run(year: int):
    year_dir = OUTPUTS_DIR / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)

    print(f"▶ Procesando año {year}")

    parametros = normalize_all(year)

    json_out = year_dir / "parametros_arca.json"
    json_out.write_text(
        json.dumps(parametros, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"✅ JSON generado: {json_out}")

    update_excel(json_out, EXCEL_PATH)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()
    run(args.year)


if __name__ == "__main__":
    cli()
