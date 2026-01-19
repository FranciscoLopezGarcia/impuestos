import json
from pathlib import Path
from utils import to_number
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"


def normalize_bp_minimo(year_filter=None):
    """
    Normaliza el mínimo no imponible de Bienes Personales.
    
    Estructura esperada del JSON:
    {
      "anio": 2024,
      "fuente": "ARCA",
      "minimo_no_imponible": "$ 292.994.964,89"
    }
    
    Args:
        year_filter (int, optional): Si se especifica, solo procesa ese año.
    
    Returns:
        list: Lista de registros normalizados
    """
    out = []
    
    # Si hay filtro de año, buscar solo ese archivo
    if year_filter:
        years_to_process = [year_filter]
    else:
        # Sin filtro, buscar todos los archivos disponibles
        pattern = "raw_bp_determinativa_*.json"
        files = sorted(RAW_DIR.glob(pattern))
        years_to_process = []
        for f in files:
            # Extraer año del nombre: raw_bp_determinativa_2024.json -> 2024
            try:
                year = int(f.stem.split('_')[-1])
                years_to_process.append(year)
            except ValueError:
                continue
    
    # Procesar cada año
    for year in years_to_process:
        raw_file = RAW_DIR / f"raw_bp_determinativa_{year}.json"
        
        if not raw_file.exists():
            continue
        
        try:
            data = json.loads(raw_file.read_text(encoding="utf-8"))
            
            # Estructura: {"anio": 2024, "fuente": "ARCA", "minimo_no_imponible": "$ 292.994.964,89"}
            minimo = data.get("minimo_no_imponible")
            
            out.append({
                "concepto": "BP_MINIMO_NO_IMPONIBLE",
                "impuesto": "BIENES_PERSONALES",
                "anio": data.get("anio", year),
                "valor_raw": minimo,
                "valor_num": to_number(minimo),
                "unidad": "ARS",
                "fuente": data.get("fuente", "ARCA"),
                "origen": "HTML_DETERMINATIVA",
                "url": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/declaracion-jurada/determinativa.asp",
            })
        except Exception as e:
            print(f"⚠️  Error procesando {raw_file.name}: {e}")
            continue
    
    return out


# Para testing
if __name__ == "__main__":
    print("=" * 60)
    print("TEST: normalize_bp_minimo")
    print("=" * 60)
    
    # Test 1: Todos los años
    print("\n1️⃣  Test: Todos los años")
    todos = normalize_bp_minimo()
    print(f"   Total registros: {len(todos)}")
    for param in todos:
        print(f"   • Año {param['anio']}: {param['valor_raw']}")
    
    # Test 2: Solo 2024
    print("\n2️⃣  Test: Solo año 2024")
    solo_2024 = normalize_bp_minimo(year_filter=2024)
    print(f"   Total registros: {len(solo_2024)}")
    for param in solo_2024:
        print(f"   • Año {param['anio']}: {param['valor_raw']}")
    
    print("\n" + "=" * 60)