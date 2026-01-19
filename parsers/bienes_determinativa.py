import json
import re
import requests
from bs4 import BeautifulSoup, Tag
from pathlib import Path

URL = "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/declaracion-jurada/determinativa.asp"

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT = RAW_DIR / "raw_bp_determinativa.json"


HEADERS = {"User-Agent": "Impuestos-Explorer"}

# Regex robustos (AR $ con separadores argentinos)
RE_PERIODO = re.compile(r"per[ií]odo\s+(20\d{2})", re.IGNORECASE)
RE_MONEY = re.compile(r"\$\s*[\d\.\,]+")  # "$ 292.994.964,89"


def clean_text(txt: str) -> str:
    return re.sub(r"\s+", " ", (txt or "")).strip()


def build_xpath(el: Tag) -> str:
    """
    XPath simple (aproximado) para debug.
    Ej: /html/body/main/section[1]/div[1]/div[1]/article[1]/ul[1]/li[1]
    """
    parts = []
    cur = el
    while cur and isinstance(cur, Tag):
        name = cur.name
        if name in ("[document]",):
            break

        # índice entre hermanos del mismo tag
        idx = 1
        sib = cur
        while sib.previous_sibling:
            sib = sib.previous_sibling
            if isinstance(sib, Tag) and sib.name == name:
                idx += 1

        parts.append(f"{name}[{idx}]")
        cur = cur.parent

        if cur and isinstance(cur, Tag) and cur.name == "html":
            parts.append("html[1]")
            break

    return "/" + "/".join(reversed(parts))


def extract_amount_from_li(li: Tag) -> str | None:
    # Preferimos <strong> (como tu ejemplo)
    strong = li.find("strong")
    if strong:
        s = clean_text(strong.get_text())
        if RE_MONEY.search("$ " + s) or s.startswith("$"):
            return s if s.startswith("$") else f"$ {s}"

    # Fallback: buscar en el texto completo del li
    txt = clean_text(li.get_text(" ", strip=True))
    m = RE_MONEY.search(txt)
    return m.group(0) if m else None


def parse():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    # ✅ Arregla el “DeclaraciÃ³n” y similares
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = r.apparent_encoding or "utf-8"

    soup = BeautifulSoup(r.text, "html.parser")

    # 1) Captura de items críticos: <li> "Para el período XXXX: $ ..."
    thresholds = []
    for li in soup.find_all("li"):
        li_txt = clean_text(li.get_text(" ", strip=True))
        y = RE_PERIODO.search(li_txt)
        if not y:
            continue

        year = int(y.group(1))
        amount = extract_amount_from_li(li)

        thresholds.append({
            "year": year,
            "amount_raw": amount,              # "$ 292.994.964,89"
            "text": li_txt,                    # texto completo
            "xpath": build_xpath(li),          # debug/rastreo
        })

    # 2) Bloques generales (raw) por si hay otros montos útiles fuera de <li>
    text_blocks = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        t = clean_text(tag.get_text(" ", strip=True))
        if t:
            text_blocks.append({"type": tag.name, "text": t})

    # 3) Años detectados (de todo el texto)
    full_text = " ".join(b["text"] for b in text_blocks)
    years_detected = sorted(set(int(x) for x in re.findall(r"20\d{2}", full_text)))

    result = {
        "source": URL,
        "thresholds": thresholds,     # <-- lo importante
        "years_detected": years_detected,
        "text_blocks": text_blocks,   # raw completo (por si hay más)
    }

    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print("✅ Parser BP determinativa ejecutado")
    print(f"Archivo generado: {OUT.resolve()}")
    print(f"Thresholds encontrados: {len(thresholds)}")
    if thresholds:
        print("Ejemplo:", thresholds[0])


if __name__ == "__main__":
    parse()
