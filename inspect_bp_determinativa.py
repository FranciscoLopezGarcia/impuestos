import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

BASE_URL = "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/declaracion-jurada/determinativa.asp"
HEADERS = {"User-Agent": "Impuestos-Explorer"}

OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

OUT_TXT = OUT_DIR / "inspect_bp_determinativa.txt"

KEYWORDS = [
    "mínimo",
    "minimo",
    "exento",
    "exención",
    "casa",
    "habitacion",
    "habitación"
]

def inspect_page(url, soup, label):
    lines = []
    text = soup.get_text("\n", strip=True)

    lines.append(f"\n=== {label} ===")
    lines.append(f"URL: {url}\n")

    for line in text.splitlines():
        l = line.lower()
        if any(k in l for k in KEYWORDS):
            lines.append(line)

    # links relevantes
    lines.append("\n--- LINKS INTERNOS ---")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "bienes-personales" in href or "documentos" in href:
            lines.append(urljoin(url, href))

    return lines

def main():
    r = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    output = []
    output.extend(inspect_page(BASE_URL, soup, "PÁGINA PRINCIPAL"))

    # inspeccionamos links internos directos (1 nivel)
    links = set(
        urljoin(BASE_URL, a["href"])
        for a in soup.find_all("a", href=True)
        if "bienes-personales" in a["href"]
    )

    for link in sorted(links):
        try:
            r = requests.get(link, headers=HEADERS, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            output.extend(inspect_page(link, soup, "LINK INTERNO"))
        except Exception as e:
            output.append(f"\nERROR en {link}: {e}")

    OUT_TXT.write_text("\n".join(output), encoding="utf-8")
    print(f"OK → {OUT_TXT}")

if __name__ == "__main__":
    main()
