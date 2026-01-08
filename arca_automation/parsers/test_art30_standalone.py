"""Test standalone del parser Art.30 v2.0"""
from pathlib import Path
from art30_parser import Art30Parser
import json

# AJUSTÁ ESTA RUTA A DONDE TENÉS LOS PDFs
PDF_DIR = Path("C:/Users/franl/Desktop/impuestos/files")
YEAR = 2024

print("=" * 80)
print(f"TEST 1: Parser Art.30 v2.0 - Year {YEAR}")
print("=" * 80)

try:
    # Crear parser
    parser = Art30Parser(year=YEAR, pdf_dir=PDF_DIR)
    
    # Parsear
    result = parser.parse()
    
    # Verificar estructura
    assert 'anio' in result, "Falta campo 'anio'"
    assert 'fuente' in result, "Falta campo 'fuente'"
    assert 'items' in result, "Falta campo 'items'"
    assert isinstance(result['items'], dict), "'items' debe ser dict"
    
    # Mostrar resultados
    print(f"\n✅ Parser funcionó correctamente")
    print(f"   Año: {result['anio']}")
    print(f"   Fuente: {result['fuente']}")
    print(f"   Items encontrados: {len(result['items'])}")
    
    print("\n📊 VALORES PARSEADOS:")
    for concepto, valor in result['items'].items():
        print(f"   {concepto:30s}: {valor:>15,.2f}")
    
    # Guardar para inspección
    output_file = Path("test_output_art30.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Salida guardada en: {output_file}")
    print("\n" + "=" * 80)
    print("✅ TEST 1 PASÓ - Parser Art.30 funciona")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ TEST 1 FALLÓ")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)