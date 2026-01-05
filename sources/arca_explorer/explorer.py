import argparse
import time
import requests
import pdfplumber
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser

from config import (
    SOURCES_DIR,
    REPORTS_DIR,
    ARCA_URLS,
    KEYWORDS,
)

# =========================
# CONFIG GENERAL
# =========================

USER_AGENT = "TGA-Impuestos-Explorer"
HEADERS = {
    "User-Agent": USER_AGENT
}

DEFAULT_DELAY = 1.0  # segundos entre requests


# =========================
# ROBOTS.TXT
# =========================

def get_robots_parser(base_url: str):
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()

    return rp, robots_url


def can_fetch(rp: robotparser.RobotFileParser, url: str) -> bool:
    return rp.can_fetch(USER_AGENT, url)


def get_delay(rp: robotparser.RobotFileParser) -> float:
    rr = rp.request_rate("*")
    if rr and rr.requests and rr.seconds and rr.requests > 0:
        return rr.seconds / rr.requests
    return DEFAULT_DELAY


# =========================
# FILESYSTEM
# =========================

def ensure_dirs(year: str):
    base = SOURCES_DIR / year
    html_dir = base / "html"
    pdf_dir = base / "pdf"

    html_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    return html_dir, pdf_dir


# =========================
# HTTP HELPERS
# =========================

def safe_get(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        return r
    except Exception as e:
        return None


def download_html(name: str, url: str, html_dir: Path):
    r = safe_get(url)
    if not r or r.status_code != 200:
        return None, r.status_code if r else "ERROR"

    path = html_dir / f"{name}.html"
    path.write_text(r.text, encoding="utf-8")
    return path, 200


def extract_pdf_links(html_path: Path, base_url: str):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().endswith(".pdf"):
            full_url = urljoin(base_url, href)
            links.append(full_url)

    return list(set(links))


def download_pdf(url: str, pdf_dir: Path):
    name = url.split("/")[-1]
    path = pdf_dir / name

    if path.exists():
        return path, "CACHED"

    r = safe_get(url)
    if not r or r.status_code != 200:
        return None, r.status_code if r else "ERROR"

    path.write_bytes(r.content)
    return path, 200


# =========================
# PDF ANALYSIS
# =========================

def analyze_pdf(pdf_path: Path):
    result = {
        "has_text": False,
        "keywords": [],
        "pages": 0,
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            result["pages"] = len(pdf.pages)
            full_text = ""

            for page in pdf.pages:
                full_text += page.extract_text() or ""

            if full_text.strip():
                result["has_text"] = True
                for kw in KEYWORDS:
                    if kw.lower() in full_text.lower():
                        result["keywords"].append(kw)

    except Exception as e:
        result["error"] = str(e)

    return result


# =========================
# MAIN ARCA EXPLORER
# =========================

def run_arca(year: str):
    html_dir, pdf_dir = ensure_dirs(year)

    rp, robots_url = get_robots_parser("https://www.arca.gob.ar/")
    delay = get_delay(rp)

    report = []
    report.append(f"[ARCA EXPLORER] Año {year}")
    report.append(f"User-Agent: {USER_AGENT}")
    report.append(f"robots.txt: {robots_url}")
    report.append(f"delay_s: {delay:.2f}")
    report.append("")

    for name, url in ARCA_URLS.items():
        report.append(f"\n=== Página índice: {name} ===")
        report.append(f"URL: {url}")

        if not can_fetch(rp, url):
            report.append("❌ BLOQUEADO por robots.txt")
            continue

        time.sleep(delay)
        html_path, status = download_html(name, url, html_dir)

        if status != 200 or not html_path:
            report.append(f"⚠️ No se pudo descargar HTML (status: {status})")
            continue

        report.append("✔ HTML descargado")

        pdf_links = extract_pdf_links(html_path, url)
        report.append(f"PDFs encontrados: {len(pdf_links)}")

        for pdf_url in tqdm(pdf_links, desc=f"PDFs {name}"):
            if not can_fetch(rp, pdf_url):
                report.append(f"  ❌ BLOQUEADO por robots: {pdf_url}")
                continue

            time.sleep(delay)
            pdf_path, pdf_status = download_pdf(pdf_url, pdf_dir)

            if pdf_status != 200 and pdf_status != "CACHED":
                report.append(f"  ⚠️ Error al bajar PDF ({pdf_status}): {pdf_url}")
                continue

            analysis = analyze_pdf(pdf_path)

            line = f"  ✔ {pdf_path.name} | páginas: {analysis['pages']}"

            if analysis.get("has_text"):
                line += " | TEXTO"
                if analysis["keywords"]:
                    line += f" | keywords: {', '.join(analysis['keywords'])}"
            else:
                line += " | SIN TEXTO"

            report.append(line)

    return report


# =========================
# ENTRYPOINT
# =========================

def main(year: str):
    report = run_arca(year)
    report_path = REPORTS_DIR / f"report_arca_{year}.txt"
    report_path.write_text("\n".join(report), encoding="utf-8")

    print("\nExploración ARCA finalizada.")
    print(f"Reporte generado: {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARCA Explorer (modo exploración)")
    parser.add_argument("--year", required=True, help="Año fiscal (ej: 2024, 2025)")
    args = parser.parse_args()

    main(args.year)
