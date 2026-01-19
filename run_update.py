"""
Script maestro para actualizar parámetros ARCA.

Este script orquesta todo el proceso:
1. Detecta qué años procesar
2. Ejecuta los parsers necesarios
3. Normaliza los datos
4. Actualiza el(los) Excel(s) especificado(s)

Uso:
    # Procesar año fiscal actual (2024)
    python run_update.py
    
    # Procesar año específico
    python run_update.py --year 2024
    
    # Procesar múltiples años
    python run_update.py --years 2019 2021 2024
    
    # Procesar todos los años disponibles
    python run_update.py --all-years
    
    # Actualizar Excel específico
    python run_update.py --year 2024 --excel "ruta/al/Liquidacion_2024.xlsx"
    
    # Actualizar múltiples Excels
    python run_update.py --year 2024 --excel "cliente1.xlsx" "cliente2.xlsx"
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Importar configuración
from config import (
    BASE_DIR,
    FILES_DIR,
    RAW_DIR,
    NORMALIZED_DIR,
    FISCAL_YEAR,
    get_available_years,
    get_log_path
)


class Logger:
    """Logger simple para guardar logs en archivo y consola"""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Limpiar log anterior si existe
        if self.log_path.exists():
            self.log_path.unlink()
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        
        # Consola
        print(log_line)
        
        # Archivo
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def info(self, message: str):
        self.log(message, "INFO")
    
    def warning(self, message: str):
        self.log(message, "WARN")
    
    def error(self, message: str):
        self.log(message, "ERROR")
    
    def success(self, message: str):
        self.log(message, "SUCCESS")


def import_parsers(logger: Logger):
    """Importa los módulos de parsers"""
    logger.info("Importando parsers...")
    
    parsers_dir = BASE_DIR / "parsers"
    if parsers_dir not in sys.path:
        sys.path.insert(0, str(parsers_dir))
    
    try:
        from parsers.art30 import parse as parse_art30
        from parsers.art94 import parse as parse_art94
        from parsers.monedas import parse as parse_monedas
        from parsers.bienes_alicuotas import parse as parse_bp_alicuotas
        from parsers.bienes_determinativa import parse as parse_bp_determinativa
        
        return {
            'art30': parse_art30,
            'art94': parse_art94,
            'monedas': parse_monedas,
            'bp_alicuotas': parse_bp_alicuotas,
            'bp_determinativa': parse_bp_determinativa,
        }
    except ImportError as e:
        logger.error(f"Error al importar parsers: {e}")
        return None


def run_parsers(years: list[int], logger: Logger):
    """Ejecuta los parsers para los años especificados"""
    
    logger.info("="*70)
    logger.info("FASE 1: PARSEO DE PDFs")
    logger.info("="*70)
    
    parsers = import_parsers(logger)
    if not parsers:
        return False
    
    success = True
    
    # Parsers que dependen de año
    for year in years:
        logger.info(f"\n>>> Procesando año {year}")
        
        # Art.30 - Deducciones
        logger.info("  [1/3] Art.30 - Deducciones Personales...")
        try:
            parsers['art30'](year)
            logger.success(f"      ✓ Art.30 {year} completado")
        except FileNotFoundError as e:
            logger.warning(f"      ⚠ PDF no encontrado para {year}: {e}")
        except Exception as e:
            logger.error(f"      ✗ Error en Art.30 {year}: {e}")
            success = False
        
        # Art.94 - Escalas
        logger.info("  [2/3] Art.94 - Escalas Ganancias...")
        try:
            parsers['art94'](year)
            logger.success(f"      ✓ Art.94 {year} completado")
        except FileNotFoundError as e:
            logger.warning(f"      ⚠ PDF no encontrado para {year}: {e}")
        except Exception as e:
            logger.error(f"      ✗ Error en Art.94 {year}: {e}")
            success = False
        
        # Monedas - Valuaciones
        logger.info("  [3/3] Valuaciones Moneda Extranjera...")
        try:
            # Modificar sys.argv temporalmente para el parser de monedas
            original_argv = sys.argv
            sys.argv = ['monedas.py', str(year)]
            
            parsers['monedas']()
            
            sys.argv = original_argv
            logger.success(f"      ✓ Monedas {year} completado")
        except FileNotFoundError as e:
            logger.warning(f"      ⚠ PDF no encontrado para {year}: {e}")
        except Exception as e:
            logger.error(f"      ✗ Error en Monedas {year}: {e}")
            success = False
        finally:
            sys.argv = original_argv
    
    # Parsers que NO dependen de año (traen datos de la web)
    logger.info(f"\n>>> Procesando fuentes web")
    
    logger.info("  [1/2] Bienes Personales - Alícuotas...")
    try:
        parsers['bp_alicuotas']()
        logger.success("      ✓ BP Alícuotas completado")
    except Exception as e:
        logger.error(f"      ✗ Error en BP Alícuotas: {e}")
        success = False
    
    logger.info("  [2/2] Bienes Personales - Determinativa...")
    try:
        parsers['bp_determinativa']()
        logger.success("      ✓ BP Determinativa completado")
    except Exception as e:
        logger.error(f"      ✗ Error en BP Determinativa: {e}")
        success = False
    
    return success


def run_normalizers(logger: Logger):
    """Ejecuta el proceso de normalización"""
    
    logger.info("\n" + "="*70)
    logger.info("FASE 2: NORMALIZACIÓN DE DATOS")
    logger.info("="*70)
    
    normalizers_dir = BASE_DIR / "normalizers"
    if normalizers_dir not in sys.path:
        sys.path.insert(0, str(normalizers_dir))
    
    try:
        from normalizers.normalize_all import main as normalize_all
        
        logger.info("Ejecutando normalizers...")
        normalize_all()
        
        # Verificar que se generó el JSON
        json_path = NORMALIZED_DIR / "parametros_arca.json"
        if json_path.exists():
            import json
            data = json.loads(json_path.read_text(encoding='utf-8'))
            logger.success(f"✓ Normalización completada: {len(data)} registros")
            return True
        else:
            logger.error("✗ No se generó el JSON normalizado")
            return False
    
    except Exception as e:
        logger.error(f"✗ Error en normalización: {e}")
        return False


def update_excels(excel_paths: list[Path], year: int, logger: Logger):
    """Actualiza los Excels especificados"""
    
    if not excel_paths:
        logger.info("\n⚠️  No se especificaron Excels para actualizar")
        return True
    
    logger.info("\n" + "="*70)
    logger.info("FASE 3: ACTUALIZACIÓN DE EXCELS")
    logger.info("="*70)
    
    # Importar excel_updater
    try:
        from excel_updater import update_excel
    except ImportError:
        logger.error("✗ No se pudo importar excel_updater.py")
        logger.info("  Asegurate de tener el archivo excel_updater.py en el directorio del proyecto")
        return False
    
    success = True
    
    for excel_path in excel_paths:
        logger.info(f"\nActualizando: {excel_path.name}")
        
        if not excel_path.exists():
            logger.error(f"  ✗ El archivo no existe: {excel_path}")
            success = False
            continue
        
        try:
            update_excel(excel_path, year)
            logger.success(f"  ✓ Excel actualizado correctamente")
        except Exception as e:
            logger.error(f"  ✗ Error al actualizar Excel: {e}")
            success = False
    
    return success


def main():
    """Función principal"""
    
    # Parsear argumentos
    parser = argparse.ArgumentParser(
        description="Actualiza parámetros ARCA desde PDFs oficiales",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--year',
        type=int,
        help=f'Año a procesar (default: {FISCAL_YEAR})'
    )
    
    parser.add_argument(
        '--years',
        type=int,
        nargs='+',
        help='Procesar múltiples años específicos (ej: --years 2019 2021 2024)'
    )
    
    parser.add_argument(
        '--all-years',
        action='store_true',
        help='Procesar todos los años disponibles en la carpeta de PDFs'
    )
    
    parser.add_argument(
        '--excel',
        nargs='+',
        help='Ruta(s) a Excel(s) a actualizar'
    )
    
    parser.add_argument(
        '--skip-parse',
        action='store_true',
        help='Saltar fase de parseo (usar JSONs raw existentes)'
    )
    
    parser.add_argument(
        '--skip-normalize',
        action='store_true',
        help='Saltar normalización (usar JSON normalizado existente)'
    )
    
    args = parser.parse_args()
    
    # Iniciar logger
    log_path = get_log_path("run_update")
    logger = Logger(log_path)
    
    # Banner
    logger.info("="*70)
    logger.info("ARCA AUTOMATION - ACTUALIZACIÓN DE PARÁMETROS")
    logger.info("="*70)
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log: {log_path}")
    logger.info("")
    
    # Determinar qué años procesar
    if args.all_years:
        years = get_available_years()
        if not years:
            logger.error("No se encontraron PDFs en la carpeta de archivos")
            logger.info(f"Carpeta de PDFs: {FILES_DIR}")
            return 1
        logger.info(f"Años detectados: {years}")
    
    elif args.years:
        years = args.years
        logger.info(f"Años especificados: {years}")
    
    elif args.year:
        years = [args.year]
        logger.info(f"Año especificado: {args.year}")
    
    else:
        years = [FISCAL_YEAR]
        logger.info(f"Año fiscal por defecto: {FISCAL_YEAR}")
    
    # Procesar Excels
    excel_paths = []
    if args.excel:
        for excel_str in args.excel:
            excel_path = Path(excel_str)
            if not excel_path.is_absolute():
                excel_path = BASE_DIR / excel_path
            excel_paths.append(excel_path)
        
        logger.info(f"Excels a actualizar: {len(excel_paths)}")
    
    # FASE 1: Parseo
    if not args.skip_parse:
        if not run_parsers(years, logger):
            logger.error("\n❌ FASE 1 FALLÓ: Errores en parseo")
            logger.info("Revisá los logs arriba para más detalles")
            return 1
    else:
        logger.info("\n⏭️  FASE 1 SALTADA (--skip-parse)")
    
    # FASE 2: Normalización
    if not args.skip_normalize:
        if not run_normalizers(logger):
            logger.error("\n❌ FASE 2 FALLÓ: Error en normalización")
            return 1
    else:
        logger.info("\n⏭️  FASE 2 SALTADA (--skip-normalize)")
    
    # FASE 3: Actualización de Excels
    if excel_paths:
        # Determinar qué año usar para la actualización
        update_year = years[-1]  # Usar el último año procesado
        
        if not update_excels(excel_paths, update_year, logger):
            logger.error("\n❌ FASE 3 FALLÓ: Errores al actualizar Excels")
            return 1
    else:
        logger.info("\n⏭️  FASE 3 SALTADA (no se especificaron Excels)")
    
    # Resumen final
    logger.info("\n" + "="*70)
    logger.info("RESUMEN FINAL")
    logger.info("="*70)
    logger.success("✅ PROCESO COMPLETADO CON ÉXITO")
    
    logger.info(f"\n📊 Años procesados: {years}")
    logger.info(f"📁 JSONs raw: {RAW_DIR}")
    logger.info(f"📁 JSON normalizado: {NORMALIZED_DIR / 'parametros_arca.json'}")
    
    if excel_paths:
        logger.info(f"📊 Excels actualizados: {len(excel_paths)}")
    
    logger.info(f"\n📝 Log completo: {log_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())