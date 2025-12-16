import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
from tqdm import tqdm
import time

HEADERS = {
    "User-Agent": "Impuestos-Explorer"
}

SEEDS = [
    # Ganancias
    "https://www.arca.gob.ar/gananciasYBienes/ganancias/",
    "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/",
    "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/deducciones/",
    "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/deducciones/documentos/",
    "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/declaracion-jurada/",
    "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/declaracion-jurada/documentos/",

    # Bienes Personales
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/",
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/declaracion-jurada/",
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/declaracion-jurada/determinativa.asp",
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/valuaciones/",
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/valuaciones/documentos/",
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/conceptos-basicos/",
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/conceptos-basicos/alicuotas.asp",
]

visited = set()
found_pdfs = set()

def is_internal(url: str) -> bool:
    return urlparse(url).netloc.endswith("arca.gob.ar")

def crawl(url: str, depth: int = 0, max_depth: int = 4):
    if url in visited or depth > max_depth:
        return

    visited.add(url)

    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
    except Exception:
        return

    if r.status_code != 200:
        return

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urljoin(url, href)

        if not is_internal(full_url):
            continue

        if full_url.lower().endswith(".pdf"):
            found_pdfs.add(full_url)
        else:
            crawl(full_url, depth + 1, max_depth)

    time.sleep(0.5)  # ser prolijos con ARCA

if __name__ == "__main__":
    for seed in tqdm(SEEDS, desc="Crawling dirigido ARCA"):
        crawl(seed)

    print("\nPDFs encontrados:\n")
    for pdf in sorted(found_pdfs):
        print(pdf)
