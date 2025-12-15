import argparse
import requests
import pdfplumber
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from config import (
    SOURCES_DIR,
    REPORTS_DIR,
    ARCA_URLS,
    KEYWORDS,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def ensure_dirs(year: str):
    html_dir = SOURCES_DIR / year / "html"
    pdf_dir = SOURCES_DIR / year / "pdf"
    html_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    return html_dir, pdf_dir


def download_html(name: str, url: str, html_dir: Path):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    path = html_dir / f"{name}.html"
    path.write_text(r.text, encoding="utf-8")
    return path


def extract_pdf_links(html_path: Path):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            if href.startswith("http"):
                links.append(href)
            else:
                links.append("https://www.arca.gob.ar" + href)
    return list(set(links))


def download_pdf(url: str, pdf_dir: Path):
    name = url.split("/")[-1]
    path = pdf_dir / name
    if path.exists():
        return path
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    return path


def analyze_pdf(pdf_path: Path):
    result = {
        "has_text": False,
        "keywords": [],
    }
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text

            if full_text.strip():
                result["has_text"] = True
                for kw in KEYWORDS:
                    if kw.lower() in full_text.lower():
                        result["keywords"].append(kw)
    except Exception as e:
        result["error"] = str(e)

    return result


def main(year: str):
    html_dir, pdf_dir = ensure_dirs(year)
    report_lines = []
    report_lines.append(f"[ARCA EXPLORER] Año {year}\n")

    for name, url in ARCA_URLS.items():
        report_lines.append(f"\nPágina: {name}")
        print(f"Descargando HTML: {url}")

        html_path = download_html(name, url, html_dir)
        pdf_links = extract_pdf_links(html_path)

        report_lines.append(f"  PDFs encontrados: {len(pdf_links)}")

        for pdf_url in tqdm(pdf_links, desc=f"PDFs {name}"):
            pdf_path = download_pdf(pdf_url, pdf_dir)
            analysis = analyze_pdf(pdf_path)

            line = f"    - {pdf_path.name}: "
            if analysis.get("has_text"):
                line += "TEXTO"
                if analysis["keywords"]:
                    line += f" | Keywords: {', '.join(analysis['keywords'])}"
            else:
                line += "SIN TEXTO"

            report_lines.append(line)

    report_path = REPORTS_DIR / f"report_{year}.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print("\nExploración finalizada.")
    print(f"Reporte generado: {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Explorador ARCA")
    parser.add_argument("--year", required=True, help="Año fiscal (ej: 2024, 2025)")
    args = parser.parse_args()

    main(args.year)
