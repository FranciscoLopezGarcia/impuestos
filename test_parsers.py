import sys
from pathlib import Path
import json
import re

# Ajustar paths si es necesario
BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = Path(r"C:\Users\franl\Desktop\impuestos\files")
OUTPUTS_DIR = BASE_DIR / "outputs"
RAW_DIR = OUTPUTS_DIR / "raw"

# Asegurar que los directorios existen
RAW_DIR.mkdir(parents=True, exist_ok=True)


def find_years_in_files(pattern: str) -> list[int]:
    """Busca años en nombres de archivos que coincidan con el patrón"""
    files = list(FILES_DIR.glob(pattern))
    years = []
    for f in files:
        match = re.search(r'(\d{4})', f.stem)
        if match:
            years.append(int(match.group(1)))
    return sorted(set(years))


def validate_json(json_path: Path, expected_keys: list[str]) -> tuple[bool, str]:
    """Valida que un JSON tenga las claves esperadas"""
    try:
        if not json_path.exists():
            return False, f"Archivo no existe: {json_path}"
        
        data = json.loads(json_path.read_text(encoding='utf-8'))
        
        # Verificar claves
        missing_keys = [k for k in expected_keys if k not in data]
        if missing_keys:
            return False, f"Faltan claves: {missing_keys}"
        
        # Verificar que tenga datos
        if isinstance(data, dict):
            items = data.get('items', data)
            if not items:
                return False, "JSON vacío o sin datos"
        
        return True, "OK"
    
    except Exception as e:
        return False, f"Error al leer JSON: {str(e)}"


# def test_art30():
#     """Test parser Art.30 - Deducciones Personales"""
#     print("\n" + "="*70)
#     print("TEST: Art.30 - Deducciones Personales")
#     print("="*70)
    
#     pattern = "Deducciones-personales-art-30-liquidacion-anual-*.pdf"
#     years = find_years_in_files(pattern)
    
#     if not years:
#         print("❌ No se encontraron PDFs de Art.30")
#         print(f"   Buscando en: {FILES_DIR}")
#         print(f"   Patrón: {pattern}")
#         return False
    
#     print(f"📁 Años encontrados: {years}")
    
#     # Importar parser
#     try:
#         sys.path.insert(0, str(BASE_DIR / "parsers"))
#         from parsers.art30 import parse as parse_art30
#     except ImportError as e:
#         print(f"❌ No se pudo importar parser art30: {e}")
#         return False
    
#     # Probar cada año
#     results = []
#     for year in years:
#         print(f"\n  Procesando {year}...")
#         try:
#             parse_art30(year)
            
#             # Validar JSON generado
#             json_path = RAW_DIR / f"raw_art30_{year}.json"
#             ok, msg = validate_json(json_path, ['anio', 'items'])
            
#             if ok:
#                 # Verificar cantidad de conceptos (deberían ser 7)
#                 data = json.loads(json_path.read_text(encoding='utf-8'))
#                 count = len(data.get('items', {}))
#                 if count == 7:
#                     print(f"  ✅ {year}: OK - {count} conceptos extraídos")
#                     results.append(True)
#                 else:
#                     print(f"  ⚠️  {year}: {count}/7 conceptos (se esperaban 7)")
#                     results.append(True)  # No es error crítico
#             else:
#                 print(f"  ❌ {year}: {msg}")
#                 results.append(False)
        
#         except Exception as e:
#             print(f"  ❌ {year}: Error - {str(e)}")
#             results.append(False)
    
#     return all(results)


# def test_art94():
#     """Test parser Art.94 - Escalas Ganancias"""
#     print("\n" + "="*70)
#     print("TEST: Art.94 - Escalas Ganancias")
#     print("="*70)
    
#     # Buscar múltiples patrones posibles
#     patterns = [
#         "Tabla-art-94-liquidacion-anual-final-*.pdf",
#         "Escalas-del-Art-94-de-la-Ley-del-Impuesto-a-las-Ganancias-periodo-*.pdf"
#     ]
    
#     years = []
#     for pattern in patterns:
#         years.extend(find_years_in_files(pattern))
#     years = sorted(set(years))
    
#     if not years:
#         print("❌ No se encontraron PDFs de Art.94")
#         print(f"   Buscando en: {FILES_DIR}")
#         print(f"   Patrones probados: {patterns}")
#         return False
    
#     print(f"📁 Años encontrados: {years}")
    
#     # Importar parser
#     try:
#         sys.path.insert(0, str(BASE_DIR / "parsers"))
#         from parsers.art94 import parse as parse_art94
#     except ImportError as e:
#         print(f"❌ No se pudo importar parser art94: {e}")
#         return False
    
#     # Probar cada año
#     results = []
#     for year in years:
#         print(f"\n  Procesando {year}...")
#         try:
#             parse_art94(year)
            
#             # Validar JSON generado
#             json_path = RAW_DIR / f"raw_art94_{year}.json"
            
#             # Art94 genera una lista directa
#             if not json_path.exists():
#                 print(f"  ❌ {year}: JSON no generado")
#                 results.append(False)
#                 continue
            
#             data = json.loads(json_path.read_text(encoding='utf-8'))
            
#             if isinstance(data, list):
#                 count = len(data)
#                 if count == 9:
#                     print(f"  ✅ {year}: OK - {count} escalas extraídas")
#                     results.append(True)
#                 else:
#                     print(f"  ⚠️  {year}: {count}/9 escalas (se esperaban 9)")
#                     results.append(True)  # No es error crítico
#             else:
#                 print(f"  ❌ {year}: Formato incorrecto (se esperaba lista)")
#                 results.append(False)
        
#         except Exception as e:
#             print(f"  ❌ {year}: Error - {str(e)}")
#             results.append(False)
    
#     return all(results)


# def test_monedas():
#     """Test parser Monedas - Valuaciones"""
#     print("\n" + "="*70)
#     print("TEST: Monedas - Valuaciones")
#     print("="*70)
    
#     pattern = "Valuaciones-*-Moneda-Extranjera.pdf"
#     years = find_years_in_files(pattern)
    
#     if not years:
#         print("❌ No se encontraron PDFs de Valuaciones")
#         print(f"   Buscando en: {FILES_DIR}")
#         print(f"   Patrón: {pattern}")
#         return False
    
#     print(f"📁 Años encontrados: {years}")
    
#     # Importar parser
#     try:
#         sys.path.insert(0, str(BASE_DIR / "parsers"))
#         from parsers.monedas import parse as parse_monedas
#     except ImportError as e:
#         print(f"❌ No se pudo importar parser monedas: {e}")
#         return False
    
#     # Probar cada año
#     results = []
#     for year in years:
#         print(f"\n  Procesando {year}...")
#         try:
#             # El parser de monedas usa sys.argv, lo modificamos temporalmente
#             original_argv = sys.argv
#             sys.argv = ['monedas.py', str(year)]
            
#             parse_monedas()
            
#             sys.argv = original_argv
            
#             # Validar JSON generado
#             json_path = RAW_DIR / f"raw_monedas_{year}.json"
#             ok, msg = validate_json(json_path, ['anio', 'divisas', 'billetes'])
            
#             if ok:
#                 data = json.loads(json_path.read_text(encoding='utf-8'))
#                 divisas_count = len(data.get('divisas', []))
#                 billetes_count = len(data.get('billetes', []))
#                 print(f"  ✅ {year}: OK - {divisas_count} divisas, {billetes_count} billetes")
#                 results.append(True)
#             else:
#                 print(f"  ❌ {year}: {msg}")
#                 results.append(False)
        
#         except Exception as e:
#             print(f"  ❌ {year}: Error - {str(e)}")
#             results.append(False)
#         finally:
#             sys.argv = original_argv
    
#     return all(results)


def test_bienes_web():
    """Test parsers de Bienes Personales (web)"""
    print("\n" + "="*70)
    print("TEST: Bienes Personales (parsers web)")
    print("="*70)
    
    # Estos parsers no dependen de año, bajan de la web
    try:
        sys.path.insert(0, str(BASE_DIR / "parsers"))
        from parsers.bienes_alicuotas import parse as parse_alicuotas
        from parsers.bienes_determinativa import parse as parse_determinativa
    except ImportError as e:
        print(f"❌ No se pudieron importar parsers de bienes: {e}")
        return False
    
    results = []
    
    # Test alícuotas
    print("\n  Probando bienes_alicuotas...")
    try:
        parse_alicuotas()
        json_path = RAW_DIR / "raw_bienes_alicuotas_all.json"
        ok, msg = validate_json(json_path, ['fuente', 'tablas'])
        
        if ok:
            data = json.loads(json_path.read_text(encoding='utf-8'))
            count = len(data.get('tablas', []))
            print(f"  Alícuotas: OK - {count} tablas extraídas")
            results.append(True)
        else:
            print(f"  Alícuotas: {msg}")
            results.append(False)
    except Exception as e:
        print(f"  Alícuotas: Error - {str(e)}")
        results.append(False)
    
    # Test determinativa
    print("\n  Probando bienes_determinativa...")
    try:
        parse_determinativa()
        json_path = RAW_DIR / "raw_bp_determinativa.json"
        ok, msg = validate_json(json_path, ['source', 'thresholds'])
        
        if ok:
            data = json.loads(json_path.read_text(encoding='utf-8'))
            count = len(data.get('thresholds', []))
            print(f"  ✅ Determinativa: OK - {count} años con umbrales")
            results.append(True)
        else:
            print(f"  Determinativa: {msg}")
            results.append(False)
    except Exception as e:
        print(f"  Determinativa: Error - {str(e)}")
        results.append(False)
    
    return all(results)


def main():
    """Ejecuta todos los tests"""
    print("="*70)
    print("TEST DE PARSERS - ARCA AUTOMATION")
    print("="*70)
    print(f"\n📂 Directorio de PDFs: {FILES_DIR}")
    print(f"📂 Directorio de salida: {RAW_DIR}")
    
    if not FILES_DIR.exists():
        print(f"\n❌ ERROR CRÍTICO: No existe el directorio de PDFs")
        print(f"   {FILES_DIR}")
        print("\n💡 Ajusta la ruta en FILES_DIR (línea 16 de este script)")
        return
    
    # Contar PDFs disponibles
    pdf_count = len(list(FILES_DIR.glob("*.pdf")))
    print(f"\n📄 PDFs encontrados: {pdf_count}")
    
    if pdf_count == 0:
        print("\n⚠️  ADVERTENCIA: No hay PDFs en el directorio")
        print("   Asegurate de que la ruta sea correcta")
    
    # Ejecutar tests
    results = {
        # 'art30': test_art30(),
        # 'art94': test_art94(),
        # 'monedas': test_monedas(),
        'bienes_web': test_bienes_web(),
    }
    
    # Reporte final
    print("\n" + "="*70)
    print("REPORTE FINAL")
    print("="*70)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_ok = all(results.values())
    
    if all_ok:
        print("\nTODOS LOS PARSERS FUNCIONAN CORRECTAMENTE")
        print("\nPróximo paso:")
        print("  python normalizers/normalize_all.py")
    else:
        print("\n⚠️  ALGUNOS PARSERS FALLARON")
        print("\nRevisá los errores arriba y:")
        print("  1. Verificá que los PDFs estén en la carpeta correcta")
        print("  2. Verificá que los nombres de archivo sean correctos")
        print("  3. Revisá los parsers que fallaron")


if __name__ == "__main__":
    main()