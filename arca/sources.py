# arca/sources.py

def fuentes_oficiales(year: int):
    """
    URLs oficiales ARCA por año.
    Fuente de verdad del sistema.
    """

    return {
        "ganancias": {
            "art30_pdf": (
                f"https://www.arca.gob.ar/gananciasYBienes/ganancias/"
                f"personas-humanas-sucesiones-indivisas/deducciones/documentos/"
                f"Deducciones-personales-art-30-liquidacion-anual-{year}.pdf"
            ),
            "art94_pdf": (
                f"https://www.arca.gob.ar/gananciasYBienes/ganancias/"
                f"personas-humanas-sucesiones-indivisas/declaracion-jurada/documentos/"
                f"Tabla-art-94-liquidacion-anual-final-{year}.pdf"
            ),
        },
        "bienes": {
            "moneda_pdf": (
                f"https://www.arca.gob.ar/gananciasYBienes/bienes-personales/"
                f"valuaciones/documentos/Bienes-Personales-{year}/PDF/"
                f"Valuaciones-{year}-Moneda-Extranjera.pdf"
            ),
            "alicuotas_html": (
                "https://www.arca.gob.ar/gananciasYBienes/"
                "bienes-personales/conceptos-basicos/alicuotas.asp"
            ),
            "minimo_html": (
                "https://www.arca.gob.ar/gananciasYBienes/"
                "bienes-personales/declaracion-jurada/determinativa.asp"
            ),
        },
    }
