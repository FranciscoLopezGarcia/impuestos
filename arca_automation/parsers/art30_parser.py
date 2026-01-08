"""
Art. 30 Parser - Wrapper de Compatibilidad v2.0

Mantiene la interfaz del parser anterior pero usa internamente
el parser modular profesional v2.0.

Formato de salida compatible con ARCANormalizer:
{
    'anio': 2024,
    'fuente': 'ARCA',
    'items': {
        'ganancia_no_imponible': 3503688.17,
        'conyuge': 3299771.52,
        ...
    }
}
"""

from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Intentar importar el parser v2.0
try:
    from parsers.art30 import Art30Parser as Art30ParserV2
    V2_AVAILABLE = True
except ImportError:
    V2_AVAILABLE = False
    print("[WARNING] Parser v2.0 no disponible, usando parser legacy")


class Art30Parser:
    """
    Parser de Deducciones Personales (Art. 30).
    
    Wrapper que mantiene compatibilidad con código existente
    pero usa internamente el parser v2.0 si está disponible.
    """
    
    def __init__(
        self,
        year: int,
        pdf_dir: Optional[Path] = None,
        pdf_path: Optional[Path] = None,
        use_v2: bool = True
    ):
        """
        Inicializa parser manteniendo interfaz anterior.
        
        Args:
            year: Año fiscal
            pdf_dir: Directorio con PDFs (legacy)
            pdf_path: Path directo al PDF (legacy)
            use_v2: Usar parser v2.0 si está disponible
        """
        self.year = year
        self.pdf_dir = pdf_dir
        self.pdf_path = pdf_path
        
        # Determinar si usar v2.0
        self.use_v2 = use_v2 and V2_AVAILABLE
        
        if self.use_v2:
            # Crear instancia del parser v2.0
            self._parser_v2 = Art30ParserV2(
                year=year,
                pdf_dir=pdf_dir or (pdf_path.parent if pdf_path else Path.cwd()),
                log_dir=None  # Sin logs por defecto (compatibilidad)
            )
        else:
            # Usar parser legacy (si existía)
            self._parser_v2 = None
    
    def parse(self) -> Dict[str, Any]:
        """
        Parsea PDF y retorna diccionario.
        
        Mantiene formato compatible con ARCANormalizer:
        {
            'anio': 2024,
            'fuente': 'ARCA',
            'items': {
                'ganancia_no_imponible': 3503688.17,
                'conyuge': 3299771.52,
                ...
            }
        }
        
        Returns:
            Dict con datos parseados en formato legacy
        """
        if self.use_v2:
            # Usar parser v2.0
            result = self._parser_v2.parse(self.pdf_path)
            return self._adapt_v2_to_legacy(result)
        else:
            # Fallback a parser legacy
            return self._parse_legacy()
    
    def _adapt_v2_to_legacy(self, v2_output: Dict) -> Dict:
        """
        Adapta salida del parser v2.0 al formato esperado
        por ARCANormalizer.
        
        Args:
            v2_output: Salida del parser v2.0
        
        Returns:
            Dict en formato legacy
        """
        # Convertir formato v2.0 a formato legacy
        legacy = {
            'anio': v2_output['metadata']['year'],
            'fuente': 'ARCA',
            'items': {}
        }
        
        # Extraer valores de las deducciones
        for deduccion in v2_output.get('deducciones', []):
            concepto = deduccion['concepto']
            valor = deduccion['value']
            
            # Solo incluir si el valor fue parseado correctamente
            if valor is not None:
                legacy['items'][concepto] = valor
        
        return legacy
    
    def _parse_legacy(self) -> Dict:
        """
        Parser legacy (si existía).
        
        Placeholder para mantener compatibilidad si el v2.0 falla.
        """
        raise NotImplementedError(
            "Parser legacy no disponible. "
            "Instale el parser v2.0 o implemente parser legacy."
        )


# =============================================================================
# Funciones de utilidad para compatibilidad con código existente
# =============================================================================

def parse_art30(
    year: int,
    pdf_dir: Optional[Path] = None,
    pdf_path: Optional[Path] = None
) -> Dict:
    """
    Función legacy de compatibilidad.
    
    Args:
        year: Año fiscal
        pdf_dir: Directorio con PDFs
        pdf_path: Path al PDF específico
    
    Returns:
        Dict parseado en formato legacy
    """
    parser = Art30Parser(year, pdf_dir=pdf_dir, pdf_path=pdf_path)
    return parser.parse()


def get_deducciones(year: int, pdf_dir: Path) -> Dict:
    """
    Otra función legacy de compatibilidad.
    
    Args:
        year: Año fiscal
        pdf_dir: Directorio con PDFs
    
    Returns:
        Dict parseado
    """
    return parse_art30(year, pdf_dir=pdf_dir)