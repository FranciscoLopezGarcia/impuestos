"""
Parser para cotización de moneda extranjera (PDF).
"""
import pdfplumber
import re
from pathlib import Path
from typing import Dict, Tuple, Optional, List

from parsers.base import BaseParser


class MonedasParser(BaseParser):
    """Parser para cotización de moneda extranjera (BP)."""
    
    MONEY_RE = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2,6}")
    
    def __init__(self, year: int, files_dir: Path):
        super().__init__(year)
        self.files_dir = files_dir
        self.pdf_pattern = f"Valuaciones-{year}-Moneda-Extranjera.pdf"
    
    def parse(self) -> Dict:
        """
        Parsea el PDF de moneda extranjera.
        
        Returns:
            Dict con divisas y billetes
        """
        pdf_path = self.resolve_pdf_path(self.files_dir, self.pdf_pattern)
        
        if not pdf_path:
            raise FileNotFoundError(f"PDF de monedas no encontrado para año {self.year}")
        
        self.logger.info(f"Parseando: {pdf_path.name}")
        
        data = {
            "anio": self.year,
            "fuente": "ARCA",
            "divisas": [],
            "billetes": [],
        }
        
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            tables = page.extract_tables() or []
            
            if len(tables) < 2:
                self.logger.warning(f"Se esperaban 2 tablas, encontradas: {len(tables)}")
                return data
            
            # Tabla 0: Divisas, Tabla 1: Billetes
            data["divisas"] = self._parse_table(tables[0])
            data["billetes"] = self._parse_table(tables[1])
        
        self.logger.info(
            f"✓ Divisas: {len(data['divisas'])}, Billetes: {len(data['billetes'])}"
        )
        
        return data
    
    def _parse_table(self, table: List[list]) -> List[Dict]:
        """Parsea una tabla de monedas."""
        result = []
        
        # Saltar header
        for row in table[1:]:
            if not row:
                continue
            
            desc = (row[0] or "").strip()
            if not desc:
                continue
            
            comprador, vendedor = self._extract_two_numbers(row)
            
            result.append({
                "descripcion": desc,
                "comprador": comprador,
                "vendedor": vendedor,
            })
        
        return result
    
    def _extract_two_numbers(self, row: list) -> Tuple[Optional[str], Optional[str]]:
        """Encuentra los dos primeros valores numéricos (comprador/vendedor)."""
        nums = []
        
        for cell in row:
            if not cell:
                continue
            
            for m in self.MONEY_RE.findall(str(cell)):
                nums.append(m)
                if len(nums) >= 2:
                    break
            
            if len(nums) >= 2:
                break
        
        if len(nums) >= 2:
            return nums[0], nums[1]
        
        return None, None
