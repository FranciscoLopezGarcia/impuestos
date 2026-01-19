import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import json
import argparse

from bp_minimo import normalize_bp_minimo
from bp_alicuotas import normalize_bp_alicuotas
from bp_dolar import normalize_bp_dolar
from gan_deducciones import normalize_ganancias_deducciones
from gan_escalas import normalize_ganancias_escalas
from configs.paths import NORMALIZED_DIR


OUT = NORMALIZED_DIR / "parametros_arca.json"


def parse_args():
    """
    Parsea los argumentos de línea de comandos.
    
    Uso:
        python normalize_all.py              # Procesa todos los años
        python normalize_all.py --year 2024  # Solo procesa 2024
        python normalize_all.py --year 2025  # Solo procesa 2025
    """
    parser = argparse.ArgumentParser(
        description='Normaliza todos los parámetros fiscales de ARCA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s                    Procesa todos los años disponibles
  %(prog)s --year 2024        Procesa solo parámetros del año 2024
  %(prog)s --year 2025        Procesa solo parámetros del año 2025
        """
    )
    parser.add_argument(
        '--year',
        type=int,
        default=None,
        metavar='YYYY',
        help='Año fiscal a procesar (ej: 2024). Si no se especifica, procesa todos los años.'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 70)
    print("🔧 NORMALIZACIÓN DE PARÁMETROS FISCALES ARCA")
    print("=" * 70)
    
    if args.year:
        print(f"📅 Modo: Filtro de año activo → {args.year}")
    else:
        print("📅 Modo: Procesando todos los años disponibles")
    
    print()
    
    # Lista para acumular todos los parámetros
    parametros = []
    
    # 1. Mínimo no imponible de Bienes Personales
    print("1️⃣  Procesando: Mínimo no imponible (BP)...")
    try:
        bp_min = normalize_bp_minimo(year_filter=args.year)
        parametros.extend(bp_min)
        print(f"   ✅ {len(bp_min)} registro(s) agregado(s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Alícuotas de Bienes Personales
    print("2️⃣  Procesando: Alícuotas de Bienes Personales...")
    try:
        bp_alic = normalize_bp_alicuotas(year_filter=args.year)
        parametros.extend(bp_alic)
        print(f"   ✅ {len(bp_alic)} registro(s) agregado(s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Cotización del dólar
    print("3️⃣  Procesando: Cotización del dólar (BP)...")
    try:
        bp_dol = normalize_bp_dolar(year_filter=args.year)
        parametros.extend(bp_dol)
        print(f"   ✅ {len(bp_dol)} registro(s) agregado(s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Deducciones de Ganancias
    print("4️⃣  Procesando: Deducciones de Ganancias...")
    try:
        gan_ded = normalize_ganancias_deducciones(year_filter=args.year)
        parametros.extend(gan_ded)
        print(f"   ✅ {len(gan_ded)} registro(s) agregado(s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Escalas de Ganancias
    print("5️⃣  Procesando: Escalas de Ganancias...")
    try:
        gan_esc = normalize_ganancias_escalas(year_filter=args.year)
        parametros.extend(gan_esc)
        print(f"   ✅ {len(gan_esc)} registro(s) agregado(s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Guardar el resultado final
    print()
    print("💾 Guardando archivo normalizado...")
    
    OUT.write_text(
        json.dumps(parametros, indent=2, ensure_ascii=False), 
        encoding="utf-8"
    )
    
    # Resumen final
    print()
    print("=" * 70)
    print("✅ NORMALIZACIÓN COMPLETADA")
    print("=" * 70)
    print(f"📊 Total de registros generados: {len(parametros)}")
    
    # Mostrar desglose por año si hay múltiples años
    if not args.year:
        años_encontrados = {}
        for param in parametros:
            year = param.get('anio')
            if year:
                años_encontrados[year] = años_encontrados.get(year, 0) + 1
        
        if años_encontrados:
            print("\n📈 Desglose por año:")
            for year in sorted(años_encontrados.keys()):
                count = años_encontrados[year]
                print(f"   • {year}: {count} registro(s)")
    
    print(f"\n💾 Archivo guardado en: {OUT.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    main()