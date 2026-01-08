"""
Parser para alícuotas de Bienes Personales (HTML).
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict

from parsers.base import BaseParser
from config.settings import HTTP_HEADERS, HTTP_TIMEOUT
from config.constants import ARCA_URLS


class BPAlicuotasParser(BaseParser):
    """Parser para alícuotas de Bienes Personales (HTML)."""
    
    def __init__(self):
        super().__init__()
        self.url = ARCA_URLS["bp_alicuotas"]["url"]
    
    def parse(self) -> Dict:

        self.logger.info(f"Descargando: {self.url}")
        
        response = requests.get(self.url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")
        
        data = {
            "fuente": "ARCA",
            "tablas": []
        }
        
        for idx, table in enumerate(tables):
            rows = []
            for tr in table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
                if cells:
                    rows.append(cells)
            
            data["tablas"].append({
                "index": idx,
                "rows": rows
            })
        
        self.logger.info(f"✓ {len(data['tablas'])} tablas extraídas")
        return data
