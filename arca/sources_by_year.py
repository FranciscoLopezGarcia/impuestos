def sources_for_year(year: int):
    y = str(year)

    return {
        "art30": [
            f"https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/deducciones/documentos/"
            f"Deducciones-personales-art-30-liquidacion-anual-{y}.pdf"
        ],
        "art94": [
            f"https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/declaracion-jurada/documentos/"
            f"Tabla-art-94-liquidacion-anual-final-{y}.pdf"
        ],
        "moneda": [
            f"https://www.arca.gob.ar/gananciasYBienes/bienes-personales/valuaciones/documentos/"
            f"Bienes-Personales-{y}/PDF/Valuaciones-{y}-Moneda-Extranjera.pdf"
        ],
        "html": {
            "bp_alicuotas": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/conceptos-basicos/alicuotas.asp",
            "bp_determinativa": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/declaracion-jurada/determinativa.asp",
        }
    }
