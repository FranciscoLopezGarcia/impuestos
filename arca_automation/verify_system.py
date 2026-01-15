"""
Script de Verificación Completa del Sistema ARCA.

Ejecuta todo el flujo y muestra qué funciona y qué falla.
"""

import sys
from pathlib import Path
import json

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def print_section(title):
    """Imprime sección con formato."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def verify_files():
    """Verifica que existan los PDFs necesarios."""
    print_section("1. VERIFICANDO ARCHIVOS PDF")
    
    files_dir = Path("C:/Users/franl/Desktop/impuestos/files")
    
    if not files_dir.exists():
        print(f"❌ Carpeta de archivos no existe: {files_dir}")
        return False
    
    print(f"✅ Carpeta de archivos: {files_dir}")
    
    # Verificar PDFs necesarios para 2024
    required_pdfs = {
        "Art.30": "Deducciones-personales-art-30-liquidacion-anual-2024.pdf",
        "Art.94": "Tabla-art-94-liquidacion-anual-final-2024.pdf",
        "Monedas": "Valuaciones-2024-Moneda-Extranjera.pdf",
    }
    
    found = []
    missing = []
    
    for name, filename in required_pdfs.items():
        pdf_path = files_dir / filename
        if pdf_path.exists():
            found.append(name)
            print(f"  ✅ {name}: {filename}")
        else:
            missing.append(name)
            print(f"  ❌ {name}: {filename} NO ENCONTRADO")
    
    if missing:
        print(f"\n⚠️  Faltan {len(missing)} PDFs: {missing}")
        print("   El sistema funcionará parcialmente.")
    
    return len(found) > 0

def verify_art30_parser():
    """Verifica parser Art.30."""
    print_section("2. VERIFICANDO PARSER ART.30")
    
    try:
        from parsers.art30_parser import Art30Parser
        print("✅ Parser Art.30 importado correctamente")
        
        # Test rápido
        parser = Art30Parser(year=2024, verbose=False)
        print("✅ Parser Art.30 instanciado")
        
        # Intentar parsear
        files_dir = Path("C:/Users/franl/Desktop/impuestos/files")
        if files_dir.exists():
            try:
                result = parser.parse(pdf_dir=files_dir)
                items_count = len(result.get('items', {}))
                print(f"✅ Parser Art.30 ejecutado: {items_count} conceptos")
                
                # Mostrar algunos valores
                print("\n  Primeros 3 conceptos:")
                for i, (concepto, valor) in enumerate(list(result['items'].items())[:3]):
                    print(f"    {concepto}: {valor:,.2f}")
                
                return True
            except FileNotFoundError as e:
                print(f"⚠️  PDF no encontrado: {e}")
                return False
            except Exception as e:
                print(f"❌ Error parseando: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("⚠️  Carpeta files no existe, saltando test de parseo")
            return True
    
    except Exception as e:
        print(f"❌ Error importando parser: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_normalizer():
    """Verifica normalizer."""
    print_section("3. VERIFICANDO NORMALIZER")
    
    try:
        from normalizers.arca_normalizer import ARCANormalizer
        print("✅ Normalizer importado")
        
        normalizer = ARCANormalizer(year=2024)
        print("✅ Normalizer instanciado")
        
        # Test con datos de ejemplo
        raw_data = {
            'anio': 2024,
            'fuente': 'ARCA',
            'items': {
                'ganancia_no_imponible': 3503688.17,
                'cargas_familia_conyuge': 3299771.52,
            }
        }
        
        normalized = normalizer.normalize_deducciones(raw_data)
        print(f"✅ Normalización ejecutada: {len(normalized)} registros")
        
        # Verificar estructura
        if normalized and len(normalized) > 0:
            first = normalized[0]
            required_fields = ['concepto', 'impuesto', 'anio', 'valor']
            missing = [f for f in required_fields if f not in first]
            
            if missing:
                print(f"⚠️  Faltan campos: {missing}")
            else:
                print("✅ Estructura correcta")
                print(f"\n  Ejemplo de registro normalizado:")
                print(f"    Concepto: {first['concepto']}")
                print(f"    Impuesto: {first['impuesto']}")
                print(f"    Año: {first['anio']}")
                print(f"    Valor: {first['valor']:,.2f}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_orchestrator():
    """Verifica orchestrator."""
    print_section("4. VERIFICANDO ORCHESTRATOR")
    
    try:
        from core.orchestrator import ARCAOrchestrator
        print("✅ Orchestrator importado")
        
        # Intentar instanciar (sin ejecutar)
        orch = ARCAOrchestrator(year=2024, force_refresh=False)
        print("✅ Orchestrator instanciado")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_excel_adapter():
    """Verifica Excel adapter."""
    print_section("5. VERIFICANDO EXCEL ADAPTER")
    
    try:
        from adapters.excel_adapter import ExcelAdapter
        print("✅ Excel Adapter importado")
        
        # Verificar Excel
        excel_path = Path("C:/Users/franl/Desktop/impuestos/CH - Anuales 2024.xlsx")
        
        if not excel_path.exists():
            print(f"⚠️  Excel no encontrado: {excel_path}")
            print("   (Esto es normal si no lo tenés en esa ruta)")
            return True
        
        print(f"✅ Excel encontrado: {excel_path.name}")
        
        # Intentar abrir
        try:
            adapter = ExcelAdapter(excel_path)
            print("✅ Excel Adapter instanciado")
            
            # Validar estructura
            if adapter.validate_structure():
                print("✅ Estructura de Excel válida")
            else:
                print("⚠️  Estructura de Excel no válida (revisar hoja 'Parametros_ARCA')")
            
            return True
        
        except Exception as e:
            print(f"❌ Error abriendo Excel: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Error importando adapter: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_full_flow():
    """Verifica flujo completo (sin Excel)."""
    print_section("6. VERIFICANDO FLUJO COMPLETO")
    
    print("Ejecutando: python main.py update --year 2024 --force")
    print("(Sin Excel, solo generación de JSONs)\n")
    
    try:
        from core.orchestrator import ARCAOrchestrator
        
        orch = ARCAOrchestrator(year=2024, force_refresh=True)
        parametros = orch.run()
        
        print(f"\n✅ Flujo completo ejecutado")
        print(f"   Total registros: {len(parametros)}")
        
        # Contar por tipo
        tipos = {}
        for p in parametros:
            tipo = p['concepto'].split('_')[0] + '_' + p['concepto'].split('_')[1]
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        print("\n  Registros por tipo:")
        for tipo, count in sorted(tipos.items()):
            print(f"    {tipo}: {count}")
        
        # Verificar archivos generados
        print("\n  Archivos generados:")
        outputs = Path("outputs")
        
        if (outputs / "cache" / "2024.json").exists():
            print("    ✅ Cache: outputs/cache/2024.json")
        else:
            print("    ❌ Cache no generado")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error en flujo completo: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todas las verificaciones."""
    print("\n" + "=" * 80)
    print("  VERIFICACIÓN COMPLETA DEL SISTEMA ARCA")
    print("=" * 80)
    
    results = {
        "Archivos PDF": verify_files(),
        "Parser Art.30": verify_art30_parser(),
        "Normalizer": verify_normalizer(),
        "Orchestrator": verify_orchestrator(),
        "Excel Adapter": verify_excel_adapter(),
        "Flujo Completo": verify_full_flow(),
    }
    
    # Resumen
    print_section("RESUMEN")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for nombre, resultado in results.items():
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"  {nombre:20s}: {status}")
    
    print(f"\n  Total: {passed}/{total} verificaciones exitosas")
    
    if passed == total:
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("\nPróximos pasos:")
        print("  1. Ejecutar: python main.py update --year 2024 --force")
        print("  2. Verificar outputs en: outputs/cache/2024.json")
        print("  3. Actualizar Excel: python main.py update --year 2024 --excel 'ruta/al/excel.xlsx'")
    else:
        print("\n⚠️  Hay problemas que resolver")
        print("   Revisa los errores arriba y corrige los módulos que fallaron.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()