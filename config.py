"""
Configuración centralizada del proyecto ARCA Automation.

IMPORTANTE: Ajusta estas rutas según tu entorno.
"""

from pathlib import Path
from datetime import datetime


# ============================================================================
# CONFIGURACIÓN PRINCIPAL
# ============================================================================

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Directorio con los PDFs originales de ARCA
# ⚠️ AJUSTA ESTA RUTA SEGÚN TU PC
FILES_DIR = Path(r"C:\Users\franl\Desktop\impuestos\files")

# Año fiscal por defecto (se calcula automáticamente)
# El año fiscal es el año anterior al actual
# Ejemplo: En 2025, el año fiscal es 2024
CURRENT_YEAR = datetime.now().year
FISCAL_YEAR = CURRENT_YEAR - 1

# Rango de años de interés (desde 2019 en adelante)
MIN_YEAR = 2019
MAX_YEAR = CURRENT_YEAR


# ============================================================================
# DIRECTORIOS DE SALIDA
# ============================================================================

# Directorio principal de outputs
OUTPUTS_DIR = BASE_DIR / "outputs"

# JSONs crudos de parsers
RAW_DIR = OUTPUTS_DIR / "raw"

# JSON normalizado final
NORMALIZED_DIR = OUTPUTS_DIR / "normalized"

# Backups de Excels
BACKUPS_DIR = OUTPUTS_DIR / "backups"

# Logs
LOGS_DIR = OUTPUTS_DIR / "logs"


# ============================================================================
# CONFIGURACIÓN DE SHAREPOINT (FUTURO)
# ============================================================================

# Base URL de SharePoint (dejar None si no se usa todavía)
SHAREPOINT_BASE_URL = None

# Ruta relativa en SharePoint donde están los Excels de clientes
SHAREPOINT_CLIENTS_PATH = None


# ============================================================================
# PATRONES DE ARCHIVOS
# ============================================================================

# Patrones para encontrar PDFs por tipo
PDF_PATTERNS = {
    'art30': [
        "Deducciones-personales-art-30-liquidacion-anual-*.pdf",
        "Deducciones-del-artculo-30-de-la-Ley-del-Impuesto-a-las-Ganancias-para-el-Período-*.pdf"
    ],
    'art94': [
        "Tabla-art-94-liquidacion-anual-final-*.pdf",
        "Escalas-del-Art-94-de-la-Ley-del-Impuesto-a-las-Ganancias-periodo-*.pdf"
    ],
    'monedas': [
        "Valuaciones-*-Moneda-Extranjera.pdf"
    ]
}


# ============================================================================
# CONFIGURACIÓN DEL EXCEL
# ============================================================================

# Nombre de la hoja con parámetros
PARAMS_SHEET_NAME = "Parametros_ARCA"

# Mapeo de columnas en la hoja de parámetros
EXCEL_COLUMNS = {
    "concepto": "CONCEPTO",
    "impuesto": "IMPUESTO",
    "anio": "AÑO",
    "valor_num": "VALOR",
    "desde": "DESDE",
    "hasta": "HASTA",
    "monto_fijo": "MONTO_FIJO",
    "porcentaje": "PORCENTAJE",
    "excedente_desde": "EXCEDENTE_DESDE",
    "unidad": "UNIDAD",
    "fuente": "FUENTE",
    "origen": "ORIGEN",
}

# Columnas que son numéricas (para formateo)
NUMERIC_COLUMNS = {
    "VALOR", 
    "DESDE", 
    "HASTA", 
    "MONTO_FIJO", 
    "EXCEDENTE_DESDE", 
    "PORCENTAJE"
}


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def ensure_directories():
    """Crea los directorios necesarios si no existen"""
    for directory in [OUTPUTS_DIR, RAW_DIR, NORMALIZED_DIR, BACKUPS_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def validate_config():
    """Valida que la configuración sea correcta"""
    errors = []
    
    if not FILES_DIR.exists():
        errors.append(f"El directorio de PDFs no existe: {FILES_DIR}")
    
    if not BASE_DIR.exists():
        errors.append(f"El directorio base no existe: {BASE_DIR}")
    
    return errors


# ============================================================================
# HELPERS
# ============================================================================

def get_available_years() -> list[int]:
    """
    Detecta qué años hay disponibles en la carpeta de PDFs.
    Busca en todos los patrones definidos.
    """
    import re
    
    years = set()
    
    for patterns_list in PDF_PATTERNS.values():
        for pattern in patterns_list:
            for pdf_file in FILES_DIR.glob(pattern):
                # Buscar año (4 dígitos) en el nombre
                match = re.search(r'(\d{4})', pdf_file.stem)
                if match:
                    year = int(match.group(1))
                    if MIN_YEAR <= year <= MAX_YEAR:
                        years.add(year)
    
    return sorted(years)


def get_normalized_json_path() -> Path:
    """Ruta del JSON normalizado final"""
    return NORMALIZED_DIR / "parametros_arca.json"


def get_backup_path(excel_path: Path) -> Path:
    """Genera ruta de backup para un Excel"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return BACKUPS_DIR / f"{excel_path.stem}_backup_{timestamp}{excel_path.suffix}"


def get_log_path(script_name: str) -> Path:
    """Genera ruta de log para un script"""
    date_str = datetime.now().strftime("%Y%m%d")
    return LOGS_DIR / f"{script_name}_{date_str}.log"


# ============================================================================
# AUTO-INIT
# ============================================================================

# Crear directorios al importar el módulo
ensure_directories()


if __name__ == "__main__":
    # Test de configuración
    print("="*70)
    print("CONFIGURACIÓN DE ARCA AUTOMATION")
    print("="*70)
    
    print(f"\n📂 Directorios:")
    print(f"   BASE_DIR:       {BASE_DIR}")
    print(f"   FILES_DIR:      {FILES_DIR}")
    print(f"   OUTPUTS_DIR:    {OUTPUTS_DIR}")
    print(f"   RAW_DIR:        {RAW_DIR}")
    print(f"   NORMALIZED_DIR: {NORMALIZED_DIR}")
    print(f"   BACKUPS_DIR:    {BACKUPS_DIR}")
    print(f"   LOGS_DIR:       {LOGS_DIR}")
    
    print(f"\n📅 Años:")
    print(f"   Año actual:     {CURRENT_YEAR}")
    print(f"   Año fiscal:     {FISCAL_YEAR}")
    print(f"   Rango válido:   {MIN_YEAR} - {MAX_YEAR}")
    
    print(f"\n🔍 Validando configuración...")
    errors = validate_config()
    
    if errors:
        print("\n❌ ERRORES ENCONTRADOS:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Configuración OK")
        
        print(f"\n📄 Años disponibles en PDFs:")
        years = get_available_years()
        if years:
            print(f"   {years}")
        else:
            print("   ⚠️  No se encontraron PDFs")