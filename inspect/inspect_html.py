import requests
from bs4 import BeautifulSoup

URLS = [
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/conceptos-basicos/alicuotas.asp",
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/valuaciones/periodo-fiscal-2024.asp",
]

def inspect_html(url: str):
    print(f"\n=== {url} ===")

    r = requests.get(url, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    tables = soup.find_all("table")
    images = soup.find_all("img")
    text_len = len(soup.get_text(strip=True))

    print(f"Tablas HTML: {len(tables)}")
    print(f"Imágenes: {len(images)}")
    print(f"Texto total: {text_len} chars")

    if tables:
        print("✅ Datos en tablas HTML")
    elif text_len > 500:
        print("🟡 Texto HTML sin tablas")
    else:
        print("⚠️ Probable contenido gráfico")

if __name__ == "__main__":
    for url in URLS:
        inspect_html(url)
