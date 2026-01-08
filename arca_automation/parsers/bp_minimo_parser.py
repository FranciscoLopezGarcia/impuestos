"""
Parser para mínimo no imponible de Bienes Personales (HTML).
"""
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict

from parsers.base import BaseParser
from config.settings import HTTP_HEADERS, HTTP_TIMEOUT
from config.constants import ARCA_URLS


class BPMinimoParser(BaseParser):
    """Parser para mínimo no imponible de BP (HTML)."""
    
    RE_PERIODO = re.compile(r"per[ií]odo\s+(20\d{2})", re.IGNORECASE)
    RE_MONEY = re.compile(r"\$\s*[\d\.\,]+")
    
    def __init__(self):
        super().__init__()
        self.url = ARCA_URLS["bp_minimo"]["url"]
    
    def parse(self) -> Dict:

        self.logger.info(f"Descargando: {self.url}")
        
        response = requests.get(self.url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        
        # Fix encoding
        if not response.encoding or response.encoding.lower() == "iso-8859-1":
            response.encoding = response.apparent_encoding or "utf-8"
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        thresholds = []
        
        for li in soup.find_all("li"):
            li_txt = li.get_text(" ", strip=True)
            
            # Buscar año
            year_match = self.RE_PERIODO.search(li_txt)
            if not year_match:
                continue
            
            year = int(year_match.group(1))
            
            # Buscar monto
            amount = self._extract_amount(li)
            
            if amount:
                thresholds.append({
                    "year": year,
                    "amount_raw": amount,
                    "text": li_txt,
                })
        
        self.logger.info(f"✓ {len(thresholds)} umbrales extraídos")
        
        return {
            "source": self.url,
            "thresholds": thresholds,
        }
    
    def _extract_amount(self, li) -> str:
        """Extrae monto del elemento <li>."""
        # Preferir <strong>
        strong = li.find("strong")
        if strong:
            s = strong.get_text(strip=True)
            if self.RE_MONEY.search("$ " + s) or s.startswith("$"):
                return s if s.startswith("$") else f"$ {s}"
        
        # Fallback: buscar en texto completo
        txt = li.get_text(" ", strip=True)
        m = self.RE_MONEY.search(txt)
        return m.group(0) if m else None
