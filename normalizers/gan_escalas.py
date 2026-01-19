import json
from pathlib import Path
from utils import to_number
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"


def normalize_ganancias_escalas(year_filter=None):
    """
    Normaliza las escalas de Ganancias (Art. 94).
    
    Estructura esperada del JSON (array directo):
    [
      {
        "desde": "0,00",
        "hasta": "1.360.200,00",
        "monto_fijo": "0,00",
        "porcentaje": "5",
        "excedente_desde": "0,00"
      },
      ...
    ]
    
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
        pattern = "raw_art94_*.json"
        files = sorted(RAW_DIR.glob(pattern))
        years_to_process = []
        for f in files:
            # Extraer año del nombre: raw_art94_2024.json -> 2024
            try:
                year = int(f.stem.split('_')[-1])
                years_to_process.append(year)
            except ValueError:
                continue
    
    # Procesar cada año
    for year in years_to_process:
        raw_file = RAW_DIR / f"raw_art94_{year}.json"
        
        if not raw_file.exists():
            continue
        
        try:
            data = json.loads(raw_file.read_text(encoding="utf-8"))
            
            # El JSON es un array directo
            if not isinstance(data, list):
                continue
            
            for i, tramo in enumerate(data, start=1):
                out.append({
                    "concepto": f"GAN_ESCALA_TRAMO_{i}",
                    "impuesto": "GANANCIAS",
                    "anio": year,
                    "desde": to_number(tramo.get("desde")),
                    "hasta": to_number(tramo.get("hasta")),
                    "monto_fijo": to_number(tramo.get("monto_fijo")),
                    "porcentaje": to_number(tramo.get("porcentaje")),
                    "excedente_desde": to_number(tramo.get("excedente_desde")),
                    "unidad": "ARS/%",
                    "fuente": "ARCA",
                    "origen": "PDF_ART_94",
                    "url": None,
                })
        
        except Exception as e:
            print(f"⚠️  Error procesando {raw_file.name}: {e}")
            continue
    
    return out


# Para testing
if __name__ == "__main__":
    print("=" * 60)
    print("TEST: normalize_ganancias_escalas")
    print("=" * 60)
    
    # Test 1: Todos los años
    print("\n1️⃣  Test: Todos los años")
    todos = normalize_ganancias_escalas()
    print(f"   Total registros: {len(todos)}")
    
    # Agrupar por año
    años = {}
    for param in todos:
        year = param.get('anio')
        if year not in años:
            años[year] = 0
        años[year] += 1
    
    for year in sorted(años.keys()):
        print(f"   • Año {year}: {años[year]} tramos")
    
    # Test 2: Solo 2024
    print("\n2️⃣  Test: Solo año 2024")
    solo_2024 = normalize_ganancias_escalas(year_filter=2024)
    print(f"   Total registros: {len(solo_2024)}")
    for param in solo_2024[:3]:  # Mostrar primeros 3
        print(f"   • {param['concepto']}: {param['desde']} - {param['hasta']} ({param['porcentaje']}%)")
    
    print("\n" + "=" * 60)