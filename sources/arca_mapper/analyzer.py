from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pdfplumber

from config import KEYWORDS


def analyze_html(html_text: str, base_url: str):
    soup = BeautifulSoup(html_text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    tables = []
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if headers:
            tables.append(headers)

    text = soup.get_text(separator=" ").lower()
    found_keywords = [kw for kw in KEYWORDS if kw.lower() in text]

    links = set()
    pdf_links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urljoin(base_url, href)

        if full_url.endswith(".pdf"):
            pdf_links.add(full_url)
        else:
            links.add(full_url)

    return {
        "title": title,
        "tables": tables,
        "keywords": found_keywords,
        "links": list(links),
        "pdf_links": list(pdf_links),
    }


def analyze_pdf(pdf_path):
    result = {
        "pages": 0,
        "has_text": False,
        "keywords": [],
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            result["pages"] = len(pdf.pages)
            text = ""

            for page in pdf.pages:
                text += page.extract_text() or ""

            if text.strip():
                result["has_text"] = True
                lower = text.lower()
                result["keywords"] = [kw for kw in KEYWORDS if kw.lower() in lower]

    except Exception as e:
        result["error"] = str(e)

    return result
