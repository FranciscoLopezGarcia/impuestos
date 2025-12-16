import json
import requests
from collections import deque
from urllib.parse import urlparse


from tqdm import tqdm

from config import (
    BASE_DOMAIN,
    START_URLS,
    MAX_PAGES,
    MAX_DEPTH,
    USER_AGENT,
    SITE_MAP_JSON,
    SUMMARY_TXT,
)
from robots import RobotsManager
from analyzer import analyze_html, analyze_pdf


HEADERS = {"User-Agent": USER_AGENT}


def is_internal(url: str) -> bool:
    netloc = urlparse(url).netloc
    return netloc.endswith("arca.gob.ar")



def crawl():
    robots = RobotsManager("https://www.arca.gob.ar/")


    visited = set()
    queue = deque((url, 0) for url in START_URLS)


    site_map = []
    page_count = 0

    progress = tqdm(total=MAX_PAGES, desc="Crawling ARCA")

    while queue and page_count < MAX_PAGES:
        url, depth = queue.popleft()

        if url in visited or depth > MAX_DEPTH:
            continue

        if not is_internal(url):
            continue

        if not robots.can_fetch(url):
            continue

        visited.add(url)
        robots.wait()

        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
        except Exception:
            continue

        entry = {
            "url": url,
            "status": r.status_code,
            "type": None,
        }

        if r.status_code != 200:
            site_map.append(entry)
            continue

        content_type = r.headers.get("Content-Type", "").lower()

        if "text/html" in content_type:
            entry["type"] = "html"

            analysis = analyze_html(r.text, url)
            entry.update(analysis)

            for link in analysis["links"]:
                if link not in visited:
                    queue.append((link, depth + 1))

            for pdf in analysis["pdf_links"]:
                queue.append((pdf, depth + 1))

        elif "pdf" in content_type or url.lower().endswith(".pdf"):
            entry["type"] = "pdf"

            filename = url.split("/")[-1]
            path = SITE_MAP_JSON.parent / filename

            if not path.exists():
                with open(path, "wb") as f:
                    f.write(r.content)

            entry["pdf"] = analyze_pdf(path)

        site_map.append(entry)
        page_count += 1
        progress.update(1)

    progress.close()

    SITE_MAP_JSON.write_text(json.dumps(site_map, indent=2, ensure_ascii=False), encoding="utf-8")

    summary_lines = [
        f"Páginas analizadas: {len(site_map)}",
        f"HTML: {sum(1 for e in site_map if e.get('type') == 'html')}",
        f"PDFs: {sum(1 for e in site_map if e.get('type') == 'pdf')}",
    ]

    SUMMARY_TXT.write_text("\n".join(summary_lines), encoding="utf-8")


if __name__ == "__main__":
    crawl()
    print("Mapa del sitio generado.")
    print(f"- {SITE_MAP_JSON}")
    print(f"- {SUMMARY_TXT}")
