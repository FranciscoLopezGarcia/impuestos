"""
Configuración centralizada del sistema ARCA Automation.
Todos los paths y configuraciones se manejan aquí.
"""
from pathlib import Path
from datetime import datetime, timedelta
import os

# =============================================================================
# PATHS BASE
# =============================================================================

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Directorio donde están los PDFs descargados manualmente (temporal)
# TODO: Cambiar a SharePoint cuando esté listo
FILES_DIR = Path(os.getenv("ARCA_FILES_DIR", r"C:\Users\franl\Desktop\impuestos\files"))

# Directorio de outputs
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
RAW_DIR = OUTPUTS_DIR / "raw"
NORMALIZED_DIR = OUTPUTS_DIR / "normalized"
CACHE_DIR = OUTPUTS_DIR / "cache"
LOGS_DIR = OUTPUTS_DIR / "logs"

# Crear directorios si no existen
for dir_path in [RAW_DIR, NORMALIZED_DIR, CACHE_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# =============================================================================
# CONFIGURACIÓN DE CACHE
# =============================================================================

# Cache es "eterno" - se crea una vez y se usa siempre
# Solo se actualiza con --force o si no existe
CACHE_ENABLED = True
CACHE_FORMAT = "json"  # Formato de cache

# Metadata de cache
CACHE_METADATA_FILENAME = ".metadata.json"

# =============================================================================
# CONFIGURACIÓN DE DESCARGA
# =============================================================================

# URLs base de ARCA
ARCA_BASE_URL = "https://www.arca.gob.ar"

# Headers HTTP
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Timeout para requests (segundos)
HTTP_TIMEOUT = 30

# Delay entre requests (para ser respetuosos con ARCA)
REQUEST_DELAY = 1.0

# Reintentos en caso de error
MAX_RETRIES = 3
RETRY_DELAY = 2.0

# =============================================================================
# CONFIGURACIÓN DE PARSERS
# =============================================================================

# Años soportados
MIN_YEAR = 2019
MAX_YEAR = datetime.now().year + 1  # Permite año próximo

# Encoding de PDFs
PDF_ENCODING = "utf-8"

# Palabras clave para validación
VALIDATION_KEYWORDS = {
    "ganancias": ["ganancia", "deducción", "escala"],
    "bienes_personales": ["bienes", "alícuota", "mínimo"],
}

# =============================================================================
# CONFIGURACIÓN DE EXCEL
# =============================================================================

# Nombre de la hoja donde están los parámetros
EXCEL_SHEET_NAME = "Parametros ARCA"

# Fila donde empiezan los datos (después del header)
EXCEL_DATA_START_ROW = 2

# Mapeo de columnas JSON → Excel
EXCEL_COLUMN_MAP = {
    "concepto": "A",
    "impuesto": "B",
    "anio": "C",
    "valor": "D",
    "desde": "E",
    "hasta": "F",
    "monto_fijo": "G",
    "porcentaje": "H",
    "excedente_desde": "I",
    "unidad": "J",
    "fuente": "K",
    "origen": "L",
}

# Columnas que deben formatearse como números con decimales
NUMERIC_COLUMNS = {"valor", "desde", "hasta", "monto_fijo", "porcentaje", "excedente_desde"}

# Formato numérico para Excel
EXCEL_NUMBER_FORMAT = "#,##0.00"

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

# Nivel de logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Formato de logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Archivo de log (se crea uno nuevo por ejecución)
LOG_FILENAME_TEMPLATE = "arca_update_{timestamp}.log"

# =============================================================================
# CONFIGURACIÓN DE VALIDACIÓN
# =============================================================================

# Rangos esperados para valores (en millones de ARS)
VALIDATION_RANGES = {
    "GAN_DED_GANANCIA_NO_IMPONIBLE": (1.0, 20.0),
    "BP_MINIMO_NO_IMPONIBLE": (50.0, 500.0),
    "BP_DOLAR": (500.0, 2000.0),
}

# Cantidad esperada de registros por tipo
EXPECTED_COUNTS = {
    "GAN_DED": 7,  # 7 deducciones personales
    "GAN_ESCALA": 9,  # 9 tramos de escalas
    "BP_ALICUOTA_GENERAL": 4,  # 4 tramos alícuotas generales
    "BP_ALICUOTA_CUMPLIDORES": 4,  # 4 tramos cumplidores
}

# =============================================================================
# MODO DEBUG
# =============================================================================

DEBUG_MODE = os.getenv("ARCA_DEBUG", "false").lower() == "true"

if DEBUG_MODE:
    LOG_LEVEL = "DEBUG"
    print("⚠️  MODO DEBUG ACTIVADO")
