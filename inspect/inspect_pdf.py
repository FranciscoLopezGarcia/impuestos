import pdfplumber
from pathlib import Path

# Ruta base
BASE_DIR = Path(r"C:\Users\franl\Desktop\impuestos\codigo\arca_mapper\outputs")

# Archivo con las fuentes útiles
FUENTES_GANANCIAS = BASE_DIR / "fuentes_utiles_ganancias.txt"

# Carpeta donde deberían estar los PDFs descargados
PDF_DIR = BASE_DIR / "pdfs"

def inspect_pdf(path: Path):
    print(f"\n=== {path.name} ===")

    with pdfplumber.open(path) as pdf:
        total_text = 0
        tables = 0

        for page in pdf.pages:
            text = page.extract_text() or ""
            total_text += len(text)

            page_tables = page.extract_tables()
            if page_tables:
                tables += len(page_tables)

        print(f"Páginas: {len(pdf.pages)}")
        print(f"Texto extraído: {'SI' if total_text > 0 else 'NO'} ({total_text} chars)")
        print(f"Tablas detectadas: {tables}")

        if total_text == 0:
            print("⚠️ Probable PDF escaneado (OCR requerido)")
        else:
            print("✅ PDF con texto usable")

def main():
    if not FUENTES_GANANCIAS.exists():
        print("No existe fuentes_utiles_ganancias.txt")
        return

    urls = FUENTES_GANANCIAS.read_text(encoding="utf-8").splitlines()

    for url in urls:
        filename = url.split("/")[-1]
        pdf_path = PDF_DIR / filename

        if not pdf_path.exists():
            print(f"\n❌ PDF no descargado: {filename}")
            continue

        inspect_pdf(pdf_path)

if __name__ == "__main__":
    main()
