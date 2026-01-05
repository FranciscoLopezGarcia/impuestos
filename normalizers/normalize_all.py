import json
from pathlib import Path

from normalizers.bp_minimo import normalize_bp_minimo
from normalizers.bp_alicuotas import normalize_bp_alicuotas
from normalizers.bp_dolar import normalize_bp_dolar
from normalizers.gan_deducciones import normalize_ganancias_deducciones
from normalizers.gan_escalas import normalize_ganancias_escalas
from config.paths import NORMALIZED_DIR



OUT = NORMALIZED_DIR / "parametros_arca.json"


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
