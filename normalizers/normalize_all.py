import json
from pathlib import Path

from normalize_bp_minimo import normalize_bp_minimo
from normalize_bp_alicuotas import normalize_bp_alicuotas
from normalize_bp_dolar import normalize_bp_dolar
from normalize_ganancias_deducciones import normalize_ganancias_deducciones
from normalize_ganancias_escalas import normalize_ganancias_escalas

OUT = Path("../outputs/parametros_arca.json")

def main():
    parametros = []
    parametros.extend(normalize_bp_minimo())
    parametros.extend(normalize_bp_alicuotas())
    parametros.extend(normalize_bp_dolar())
    parametros.extend(normalize_ganancias_deducciones())
    parametros.extend(normalize_ganancias_escalas())

    OUT.write_text(json.dumps(parametros, indent=2, ensure_ascii=False), encoding="utf-8")

    print("✅ Parametros_ARCA generado")
    print(f"Total registros: {len(parametros)}")
    print(OUT.resolve())

if __name__ == "__main__":
    main()
