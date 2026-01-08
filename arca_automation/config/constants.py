"""
Constantes: URLs de ARCA, patrones de archivos, mapeos de conceptos.
"""

# =============================================================================
# URLs DE ARCA POR TIPO DE FUENTE
# =============================================================================

ARCA_URLS = {
    # Ganancias - Deducciones personales
    "deducciones_personales": {
        "base_url": "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/deducciones/deducciones-personales.asp",
        "pdf_pattern": "Deducciones-personales-art-30-liquidacion-anual-{year}.pdf",
        "direct_url": "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/deducciones/documentos/Deducciones-personales-art-30-liquidacion-anual-{year}.pdf",
    },
    
    # Ganancias - Escalas (Art. 94)
    "escalas_ganancias": {
        "base_url": "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/declaracion-jurada/determinacion.asp",
        "pdf_pattern": "Tabla-art-94-liquidacion-anual-final-{year}.pdf",
        "direct_url": "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/declaracion-jurada/documentos/Tabla-art-94-liquidacion-anual-final-{year}.pdf",
        # Subperíodos (ej: 2023)
        "subperiodo_patterns": [
            "Tabla-art-94-liquidacion-anual-hasta-{month}-{year}.pdf",
            "Tabla-art-94-liquidacion-anual-desde-{month}-{year}.pdf",
        ]
    },
    
    # Bienes Personales - Alícuotas (HTML)
    "bp_alicuotas": {
        "url": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/conceptos-basicos/alicuotas.asp",
        "type": "html",
    },
    
    # Bienes Personales - Mínimo no imponible (HTML)
    "bp_minimo": {
        "url": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/declaracion-jurada/determinativa.asp",
        "type": "html",
    },
    
    # Bienes Personales - Cotización dólar
    "bp_monedas": {
        "base_url": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/valuaciones/periodo-fiscal-{year}.asp",
        "pdf_pattern": "Valuaciones-{year}-Moneda-Extranjera.pdf",
        "direct_url": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/valuaciones/documentos/Valuaciones-{year}-Moneda-Extranjera.pdf",
    },
}

# =============================================================================
# SUBPERÍODOS CONOCIDOS
# =============================================================================

# Años que tienen subperíodos (escalas diferentes por período)
YEARS_WITH_SUBPERIODS = {
    2023: [
        {"name": "hasta_sep", "month": "septiembre"},
        {"name": "desde_oct", "month": "octubre"},
    ],
}

# =============================================================================
# CONCEPTOS Y MAPEOS
# =============================================================================

# Prefijos de conceptos
CONCEPT_PREFIXES = {
    "ganancias_deducciones": "GAN_DED",
    "ganancias_escalas": "GAN_ESCALA",
    "bienes_minimo": "BP_MINIMO",
    "bienes_alicuotas_general": "BP_ALICUOTA_GENERAL",
    "bienes_alicuotas_cumplidores": "BP_ALICUOTA_CUMPLIDORES",
    "bienes_dolar": "BP_DOLAR",
}

# Nombres canónicos de deducciones (Art. 30)
DEDUCCIONES_PERSONALES_KEYS = [
    "ganancia_no_imponible",
    "cargas_familia_conyuge",
    "cargas_familia_hijo",
    "cargas_familia_hijo_incapaz",
    "deduccion_especial_ap1",
    "deduccion_especial_ap1_nuevo",
    "deduccion_especial_ap2",
]

# Orden esperado de tramos en escalas (Art. 94)
ESCALAS_EXPECTED_COUNT = 9

# Orden esperado de tramos en alícuotas BP
BP_ALICUOTAS_EXPECTED_COUNT = 4  # Por régimen (general + cumplidores)

# =============================================================================
# VALIDACIÓN DE CONCEPTOS
# =============================================================================

# Conceptos obligatorios por año
REQUIRED_CONCEPTS = {
    "ganancias": [
        "GAN_DED_GANANCIA_NO_IMPONIBLE",
        "GAN_DED_DEDUCCION_ESPECIAL_AP1",
        "GAN_ESCALA_TRAMO_1",
        "GAN_ESCALA_TRAMO_9",
    ],
    "bienes_personales": [
        "BP_MINIMO_NO_IMPONIBLE",
        "BP_ALICUOTA_GENERAL_TRAMO_1",
        "BP_DOLAR_BILLETE_VEND_31_12",
    ],
}

# =============================================================================
# ORÍGENES DE DATOS
# =============================================================================

DATA_ORIGINS = {
    "PDF_ART_30": "Deducciones Personales (Art. 30)",
    "PDF_ART_94": "Escalas Ganancias (Art. 94)",
    "HTML_ALICUOTAS": "Alícuotas Bienes Personales (HTML)",
    "HTML_DETERMINATIVA": "Mínimo no imponible BP (HTML)",
    "PDF_MONEDA_EXTRANJERA": "Cotización moneda extranjera (PDF)",
}

# =============================================================================
# PALABRAS CLAVE PARA VALIDACIÓN DE PDFs
# =============================================================================

PDF_VALIDATION_KEYWORDS = {
    "art30": ["ganancia no imponible", "deducción especial", "cónyuge", "hijo"],
    "art94": ["escala", "monto fijo", "porcentaje", "excedente"],
    "monedas": ["dólar", "billete", "divisa", "comprador", "vendedor"],
}

# =============================================================================
# FUENTES (unidades)
# =============================================================================

FUENTE_DEFAULT = "ARCA"
UNIDAD_ARS = "ARS"
UNIDAD_ARS_PORCENTAJE = "ARS/%"
