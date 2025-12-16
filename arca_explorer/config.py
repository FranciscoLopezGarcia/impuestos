from pathlib import Path
import os

SOS_API_TOKEN = os.getenv("SOS_API_TOKEN")


BASE_DIR = Path(__file__).resolve().parent

SOURCES_DIR = BASE_DIR / "sources"
REPORTS_DIR = BASE_DIR / "reports"

# Palabras clave para ARCA (PDF)
KEYWORDS = [
    "Ganancia no imponible",
    "Cónyuge",
    "Hijos",
    "Deducción especial",
    "Gastos de sepelio",
    "Intereses",
    "Primas de seguros",
    "Servicio doméstico",
]

# URLs base ARCA
ARCA_URLS = {
    "deducciones_personales": "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/deducciones/deducciones-personales.asp",
    "deducciones_generales": "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/deducciones/deducciones-generales.asp",
    "bienes_personales": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/declaracion-jurada/determinativa.asp",
}

# =========================
# SOS-Contador
# =========================

SOS_BASE_URL = "https://api.sos-contador.com"


# Endpoints a explorar (NO productivos todavía)
SOS_ENDPOINTS = {
    "ganancias": "/ganancias",
    "deducciones": "/ganancias/deducciones",
    "escalas_ganancias": "/ganancias/escalas",
    "bienes_personales": "/bienes-personales",
}
