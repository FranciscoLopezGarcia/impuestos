import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"

print("=" * 70)
print("DEBUG: bp_alicuotas")
print("=" * 70)

# 1. Verificar que existe el archivo _all
RAW_ALL = RAW_DIR / "raw_bienes_alicuotas_all.json"
print(f"\n1️⃣  Archivo completo: {RAW_ALL}")
print(f"   Existe: {RAW_ALL.exists()}")

if RAW_ALL.exists():
    data_all = json.load(open(RAW_ALL, encoding='utf-8'))
    tablas = data_all.get('tablas', [])
    print(f"   Total tablas: {len(tablas)}")
    for t in tablas:
        print(f"   - Índice {t.get('index')}: {len(t.get('rows', []))} rows")

# 2. Buscar archivos por año
print(f"\n2️⃣  Archivos por año en: {RAW_DIR}")
pattern = "raw_bienes_alicuotas_*.json"
files = sorted(RAW_DIR.glob(pattern))

for f in files:
    if f.name == "raw_bienes_alicuotas_all.json":
        print(f"   [SKIP] {f.name} (archivo completo)")
        continue
    
    print(f"\n   📄 {f.name}")
    try:
        data = json.load(open(f, encoding='utf-8'))
        print(f"      anio: {data.get('anio')}")
        print(f"      fuente: {data.get('fuente')}")
        
        alicuotas = data.get('alicuotas', {})
        print(f"      alicuotas keys: {list(alicuotas.keys())}")
        
        if 'pais' in alicuotas:
            indices_pais = alicuotas['pais'].get('rows', [])
            print(f"      pais -> índices: {indices_pais}")
        
        if 'exterior' in alicuotas:
            indices_ext = alicuotas['exterior'].get('rows', [])
            print(f"      exterior -> índices: {indices_ext}")
    
    except Exception as e:
        print(f"      ❌ Error: {e}")

print("\n" + "=" * 70)