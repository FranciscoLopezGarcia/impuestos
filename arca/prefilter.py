# arca/prefilter.py

def filter_pdfs(pdf_urls: list[str], year: int):
    """
    Clasifica y selecciona PDFs oficiales de ARCA.
    NO descarta PDFs críticos.
    """

    year_str = str(year)

    ganancias = []
    bienes = []

    for url in pdf_urls:
        u = url.lower()

        # ===== GANANCIAS =====

        # Art. 30 - Deducciones personales (LIQUIDACIÓN ANUAL)
        if (
            "deducciones-personales" in u
            and "art-30" in u
            and "liquidacion-anual" in u
            and year_str in u
        ):
            ganancias.append(url)
            continue

        # Art. 94 - Escalas (LIQUIDACIÓN ANUAL / FINAL)
        if (
            "tabla-art-94" in u
            and "liquidacion" in u
            and year_str in u
        ):
            ganancias.append(url)
            continue

        # ===== BIENES PERSONALES =====

        # Moneda extranjera (PDF)
        if (
            "valuaciones" in u
            and "moneda-extranjera" in u
            and year_str in u
        ):
            bienes.append(url)
            continue

    return {
        "ganancias": sorted(set(ganancias)),
        "bienes": sorted(set(bienes)),
    }
