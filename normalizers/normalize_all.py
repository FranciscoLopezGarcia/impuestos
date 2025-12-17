from normalizers.normalize_bp_minimo import normalize_bp_minimo
from normalizers.normalize_bp_alicuotas import normalize_bp_alicuotas
from normalizers.normalize_bp_dolar import normalize_bp_dolar
from normalizers.normalize_ganancias_deducciones import normalize_ganancias_deducciones
from normalizers.normalize_ganancias_escalas import normalize_ganancias_escalas


def safe(fn):
    try:
        return fn()
    except FileNotFoundError as e:
        print(f"⚠️  RAW no encontrado, se omite: {e}")
        return []


def normalize_all(target_year: int):
    parametros = []

    blocks = [
        safe(normalize_bp_minimo),
        safe(normalize_bp_alicuotas),
        safe(normalize_bp_dolar),
        safe(normalize_ganancias_deducciones),
        safe(normalize_ganancias_escalas),
    ]

    for block in blocks:
        for p in block:
            if p.get("anio") in (None, target_year):
                parametros.append(p)

    return parametros
