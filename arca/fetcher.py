# arca/fetcher.py
import shutil
import requests
from pathlib import Path

PDF_DIR = Path(__file__).resolve().parents[1] / "outputs" / "pdfs"

def fetch_pdfs(fuentes: dict):
    if PDF_DIR.exists():
        shutil.rmtree(PDF_DIR)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    for grupo in fuentes.values():
        for nombre, url in grupo.items():
            if not url.endswith(".pdf"):
                continue

            filename = url.split("/")[-1]
            path = PDF_DIR / filename

            print(f"📥 Descargando {filename}")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            path.write_bytes(r.content)
