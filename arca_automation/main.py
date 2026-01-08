"""
Entry Point CLI - Sistema de Automatización ARCA.

Uso:
    python main.py update --year 2024 [--force] [--excel ruta/al/excel.xlsx]
    python main.py cache-info
    python main.py validate-excel ruta/al/excel.xlsx
"""
import argparse
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.orchestrator import ARCAOrchestrator
from core.cache_manager import CacheManager
from adapters.excel_adapter import ExcelAdapter
from utils.logger import get_logger, ARCALogger
from config.settings import MIN_YEAR, MAX_YEAR

logger = get_logger(__name__)


def cmd_update(args):
    """Comando: actualizar parámetros ARCA."""
    year = args.year
    force = args.force
    excel_path = args.excel
    
    # Validar año
    if not (MIN_YEAR <= year <= MAX_YEAR):
        logger.error(f"Año inválido: {year}. Rango válido: {MIN_YEAR}-{MAX_YEAR}")
        return 1
    
    try:
        # Ejecutar orquestador
        orchestrator = ARCAOrchestrator(year, force_refresh=force)
        parametros = orchestrator.run()
        
        # Si se especificó Excel, actualizarlo
        if excel_path:
            excel_path = Path(excel_path)
            if not excel_path.exists():
                logger.error(f"Excel no encontrado: {excel_path}")
                return 1
            
            logger.info(f"\n📊 Actualizando Excel: {excel_path.name}")
            adapter = ExcelAdapter(excel_path)
            adapter.update(parametros, rebuild=args.rebuild)
        
        logger.info("\n" + "="*70)
        logger.info("✓ PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("="*70)
        
        # Mostrar ruta del log
        log_file = ARCALogger.get_current_log_file()
        if log_file:
            logger.info(f"\n📝 Log completo: {log_file}")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        return 1


def cmd_update_range(args):
    """Comando: actualizar rango de años."""
    from_year = args.from_year
    to_year = args.to_year
    
    logger.info(f"Actualizando años {from_year} a {to_year}")
    
    failed_years = []
    
    for year in range(from_year, to_year + 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"AÑO {year}")
        logger.info(f"{'='*70}")
        
        try:
            orchestrator = ARCAOrchestrator(year, force_refresh=args.force)
            orchestrator.run()
        except Exception as e:
            logger.error(f"❌ Error en año {year}: {e}")
            failed_years.append(year)
    
    logger.info(f"\n{'='*70}")
    logger.info("RESUMEN")
    logger.info(f"{'='*70}")
    logger.info(f"Años procesados: {to_year - from_year + 1}")
    logger.info(f"Exitosos: {(to_year - from_year + 1) - len(failed_years)}")
    logger.info(f"Fallidos: {len(failed_years)}")
    
    if failed_years:
        logger.error(f"Años con errores: {failed_years}")
        return 1
    
    return 0


def cmd_cache_info(args):
    """Comando: mostrar información de cache."""
    info = CacheManager.get_cache_info()
    
    print("\n" + "="*70)
    print("INFORMACIÓN DE CACHE")
    print("="*70)
    
    if not info["cached_years"]:
        print("\n⚠️  No hay datos en cache")
        return 0
    
    print(f"\nTotal años en cache: {len(info['cached_years'])}")
    print(f"Tamaño total: {info['total_size_mb']:.2f} MB")
    print("\nDetalle por año:")
    print("-" * 70)
    
    for year_info in info["cached_years"]:
        print(f"\nAño {year_info['year']}:")
        print(f"  Creado: {year_info['created_at']}")
        print(f"  Registros: {year_info['record_count']}")
        print(f"  Tamaño: {year_info['size_kb']:.2f} KB")
    
    return 0


def cmd_invalidate_cache(args):
    """Comando: invalidar cache de un año."""
    year = args.year
    
    cm = CacheManager(year)
    
    if not cm.exists():
        logger.warning(f"No hay cache para año {year}")
        return 0
    
    cm.invalidate()
    logger.info(f"✓ Cache eliminado para año {year}")
    
    return 0


def cmd_validate_excel(args):
    """Comando: validar estructura de Excel."""
    excel_path = Path(args.excel)
    
    if not excel_path.exists():
        logger.error(f"Excel no encontrado: {excel_path}")
        return 1
    
    logger.info(f"Validando: {excel_path.name}")
    
    adapter = ExcelAdapter(excel_path)
    
    if adapter.validate_structure():
        logger.info("✓ Estructura válida")
        return 0
    else:
        logger.error("❌ Estructura inválida")
        return 1


def main():
    """Entry point principal."""
    parser = argparse.ArgumentParser(
        description="Sistema de Automatización ARCA - Parámetros Impositivos"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando: update
    parser_update = subparsers.add_parser("update", help="Actualizar parámetros de un año")
    parser_update.add_argument("--year", type=int, required=True, help="Año a actualizar")
    parser_update.add_argument("--force", action="store_true", help="Forzar actualización (ignorar cache)")
    parser_update.add_argument("--excel", type=str, help="Path al Excel a actualizar")
    parser_update.add_argument("--rebuild", action="store_true", help="Rebuild completo del Excel (borrar y reescribir)")
    parser_update.set_defaults(func=cmd_update)
    
    # Comando: update-range
    parser_range = subparsers.add_parser("update-range", help="Actualizar rango de años")
    parser_range.add_argument("--from", dest="from_year", type=int, required=True, help="Año inicial")
    parser_range.add_argument("--to", dest="to_year", type=int, required=True, help="Año final")
    parser_range.add_argument("--force", action="store_true", help="Forzar actualización")
    parser_range.set_defaults(func=cmd_update_range)
    
    # Comando: cache-info
    parser_cache = subparsers.add_parser("cache-info", help="Información de cache")
    parser_cache.set_defaults(func=cmd_cache_info)
    
    # Comando: invalidate-cache
    parser_invalidate = subparsers.add_parser("invalidate-cache", help="Eliminar cache de un año")
    parser_invalidate.add_argument("--year", type=int, required=True, help="Año a invalidar")
    parser_invalidate.set_defaults(func=cmd_invalidate_cache)
    
    # Comando: validate-excel
    parser_validate = subparsers.add_parser("validate-excel", help="Validar estructura de Excel")
    parser_validate.add_argument("excel", type=str, help="Path al Excel")
    parser_validate.set_defaults(func=cmd_validate_excel)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Ejecutar comando
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
