from pathlib import Path

# Archivo con la salida del crawler dirigido (pegamos ahí las URLs)
RAW_PDFS_TXT = Path("outputs/pdfs_encontrados.txt")

# Salidas
GANANCIAS_TXT = Path("outputs/fuentes_utiles_ganancias.txt")
BIENES_TXT = Path("outputs/fuentes_utiles_bienes.txt")
DESCARTADOS_TXT = Path("outputs/pdfs_descartados.txt")

# Reglas
ACEPTAR_GANANCIAS = [
    "deducciones",
    "art-30",
    "deduccion_especial",
    "valores-autonomos",
    "autonomos",
    "tope-gni",
]

ACEPTAR_BIENES = [
    "bienes-personales",
    "valuaciones",
    "alicuotas",
]

DESCARTAR = [
    "recaudacion",
    "manual",
    "institucional",
    "operadores",
    "aduaneros",
    "presentaciones",
    "plan",
    "pacto",
    "beneficio",
]

def classify(url: str) -> str:
    u = url.lower()

    if any(x in u for x in DESCARTAR):
        return "descartar"

    if any(x in u for x in ACEPTAR_GANANCIAS):
        return "ganancias"

    if any(x in u for x in ACEPTAR_BIENES):
        return "bienes"

    return "descartar"


def main():
    ganancias = []
    bienes = []
    descartados = []

    urls = RAW_PDFS_TXT.read_text(encoding="utf-8").splitlines()

    for url in urls:
        if not url.strip():
            continue

        category = classify(url)

        if category == "ganancias":
            ganancias.append(url)
        elif category == "bienes":
            bienes.append(url)
        else:
            descartados.append(url)

    GANANCIAS_TXT.write_text("\n".join(sorted(ganancias)), encoding="utf-8")
    BIENES_TXT.write_text("\n".join(sorted(bienes)), encoding="utf-8")
    DESCARTADOS_TXT.write_text("\n".join(sorted(descartados)), encoding="utf-8")

    print("Prefiltrado finalizado")
    print(f"- Ganancias:   {len(ganancias)}")
    print(f"- Bienes:      {len(bienes)}")
    print(f"- Descartados: {len(descartados)}")
    print()
    print("Archivos generados:")
    print(GANANCIAS_TXT)
    print(BIENES_TXT)
    print(DESCARTADOS_TXT)
    
def get_useful_pdfs(year: int):
    """
    Devuelve URLs de PDFs relevantes para el año indicado
    """
    ganancias = []
    bienes = []

    for pdf in all_detected_pdfs:
        url = pdf["url"]
        text = pdf["text"].lower()

        if str(year) in text:
            if "ganancias" in text or "art. 30" in text or "art. 94" in text:
                ganancias.append(url)
            if "bienes personales" in text:
                bienes.append(url)

    return {
        "ganancias": ganancias,
        "bienes": bienes
    }


if __name__ == "__main__":
    main()
