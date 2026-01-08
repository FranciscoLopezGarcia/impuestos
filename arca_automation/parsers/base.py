"""
Parser base - Clase abstracta para todos los parsers.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import re

from utils.logger import get_logger


class BaseParser(ABC):

    def __init__(self, year: Optional[int] = None):
        self.year = year
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def parse(self) -> Any:

        pass
    
    def clean_number(self, raw: str) -> str:

        if not raw or not isinstance(raw, str):
            return ""
        
        # Remover espacios
        cleaned = raw.replace(" ", "").strip()
        
        # Si ya está en formato correcto, retornar
        if re.match(r"^\d{1,3}(\.\d{3})*,\d{2}$", cleaned):
            return cleaned
        
        # Normalizar puntos múltiples
        cleaned = re.sub(r"\.{2,}", ".", cleaned)
        
        # Si tiene coma, reconstruir formato argentino
        if "," in cleaned:
            partes = cleaned.split(",", 1)
            antes_coma = partes[0]
            despues_coma = partes[1] if len(partes) > 1 else "00"
            
            # Extraer dígitos
            digitos_enteros = "".join(re.findall(r"\d", antes_coma))
            digitos_decimales = "".join(re.findall(r"\d", despues_coma))
            
            # Completar decimales si faltan
            if len(digitos_decimales) < 2:
                digitos_decimales = digitos_decimales.ljust(2, "0")
            else:
                digitos_decimales = digitos_decimales[:2]
            
            # Formatear parte entera con puntos de miles
            if len(digitos_enteros) >= 4:
                resultado = []
                for i, digito in enumerate(reversed(digitos_enteros)):
                    if i > 0 and i % 3 == 0:
                        resultado.append(".")
                    resultado.append(digito)
                
                cleaned = "".join(reversed(resultado)) + "," + digitos_decimales
            elif len(digitos_enteros) > 0:
                cleaned = digitos_enteros + "," + digitos_decimales
            else:
                return ""
        
        return cleaned if cleaned else ""
    
    def to_number(self, x) -> Optional[float]:

        if x is None:
            return None
        if isinstance(x, (int, float)):
            return float(x)
        
        s = str(x).strip()
        
        # Porcentaje
        if s.endswith("%"):
            s = s.replace("%", "").strip()
            return self.to_number(s)
        
        # Limpiar moneda y separadores
        s = s.replace("$", "").replace(" ", "")
        s = s.replace(".", "")  # miles
        s = s.replace(",", ".")  # decimal
        
        # Caso "en adelante"
        if "adelante" in s.lower():
            return None
        
        # Solo números
        if not re.search(r"\d", s):
            return None
        
        try:
            return float(s)
        except:
            return None
    
    def validate_year(self, year: int) -> bool:
        """Valida que el año sea razonable."""
        from config.settings import MIN_YEAR, MAX_YEAR
        return MIN_YEAR <= year <= MAX_YEAR
    
    def resolve_pdf_path(self, files_dir: Path, pattern: str) -> Optional[Path]:

        if self.year:
            filename = pattern.format(year=self.year)
        else:
            filename = pattern
        
        pdf_path = files_dir / filename
        
        if not pdf_path.exists():
            self.logger.warning(f"PDF no encontrado: {pdf_path}")
            return None
        
        return pdf_path
