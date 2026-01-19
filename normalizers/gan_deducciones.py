import json
from pathlib import Path
from utils import to_number
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"


def normalize_ganancias_deducciones(year_filter=None):
    """
    Normaliza las deducciones de Ganancias (Art. 30).
    
    Estructura esperada del JSON:
    {
      "anio": 2024,
      "fuente": "ARCA",
      "origen": "PDF_ART_30",
      "items": {
        "ganancia_no_imponible": "3.503.688,17",
        "cargas_familia_conyuge": "3.299.771,52",
        ...
      }
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
        pattern = "raw_art30_*.json"
        files = sorted(RAW_DIR.glob(pattern))
        years_to_process = []
        for f in files:
            # Extraer año del nombre: raw_art30_2024.json -> 2024
            try:
                year = int(f.stem.split('_')[-1])
                years_to_process.append(year)
            except ValueError:
                continue
    
    # Procesar cada año
    for year in years_to_process:
        raw_file = RAW_DIR / f"raw_art30_{year}.json"
        
        if not raw_file.exists():
            continue
        
        try:
            data = json.loads(raw_file.read_text(encoding="utf-8"))
            
            anio = data.get("anio", year)
            items = data.get("items", {})
            
            if not isinstance(items, dict):
                continue
            
            for k, v in items.items():
                out.append({
                    "concepto": f"GAN_DED_{k.upper()}",
                    "impuesto": "GANANCIAS",
                    "anio": anio,
                    "valor_raw": v,
                    "valor_num": to_number(v),
                    "unidad": "ARS",
                    "fuente": data.get("fuente", "ARCA"),
                    "origen": data.get("origen", "PDF_ART_30"),
                    "url": None,
                })
        
        except Exception as e:
            print(f"⚠️  Error procesando {raw_file.name}: {e}")
            continue
    
    return out


# Para testing
if __name__ == "__main__":
    print("=" * 60)
    print("TEST: normalize_ganancias_deducciones")
    print("=" * 60)
    
    # Test 1: Todos los años
    print("\n1️⃣  Test: Todos los años")
    todos = normalize_ganancias_deducciones()
    print(f"   Total registros: {len(todos)}")
    
    # Agrupar por año
    años = {}
    for param in todos:
        year = param.get('anio')
        if year not in años:
            años[year] = []
        años[year].append(param)
    
    for year in sorted(años.keys()):
        print(f"   • Año {year}: {len(años[year])} registros")
    
    # Test 2: Solo 2024
    print("\n2️⃣  Test: Solo año 2024")
    solo_2024 = normalize_ganancias_deducciones(year_filter=2024)
    print(f"   Total registros: {len(solo_2024)}")
    for param in solo_2024:
        print(f"   • {param['concepto']}: {param['valor_raw']}")
    
    print("\n" + "=" * 60)