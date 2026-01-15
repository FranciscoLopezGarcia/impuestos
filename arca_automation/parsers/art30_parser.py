# -*- coding: utf-8 -*-
"""
ARCA - Ganancias - Artículo 30 (Deducciones Personales) - Parser v2.0

MEJORAS v2.0:
- Detección inteligente de corrupción en números
- Validación contra rangos esperados
- Logging detallado de limpieza aplicada
- Metadata completa en salida JSON

Mantiene compatibilidad con estructura existente.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import pdfplumber


# =============================================================================
# CONFIGURACIÓN - Rangos esperados por año para validación
# =============================================================================

EXPECTED_RANGES = {
    2024: {
        "ganancia_no_imponible": (2800000, 4200000),
        "cargas_familia_conyuge": (2600000, 4000000),
        "cargas_familia_hijo": (1300000, 2000000),
        "cargas_familia_hijo_incapaz": (2600000, 4000000),
        "deduccion_especial_ap1": (9800000, 14800000),
        "deduccion_especial_ap1_nuevos": (11200000, 16900000),
        "deduccion_especial_ap2": (13400000, 20200000),
    },
    2023: {
        "ganancia_no_imponible": (361000, 542000),
        "cargas_familia_conyuge": (337000, 505000),
        "cargas_familia_hijo": (170000, 255000),
        "cargas_familia_hijo_incapaz": (340000, 510000),
        "deduccion_especial_ap1": (1264000, 1897000),
        "deduccion_especial_ap1_nuevos": (1445000, 2168000),
        "deduccion_especial_ap2": (1734000, 2602000),
    },
    # Agregar más años según necesidad
}


# =============================================================================
# Logging
# =============================================================================

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_info(msg: str) -> None:
    print(f"[{_now()}] INFO  - {msg}")

def log_warn(msg: str) -> None:
    print(f"[{_now()}] WARN  - {msg}")

def log_error(msg: str) -> None:
    print(f"[{_now()}] ERROR - {msg}")

def log_debug(msg: str, verbose: bool = False) -> None:
    if verbose:
        print(f"[{_now()}] DEBUG - {msg}")


# =============================================================================
# Mapeo de conceptos
# =============================================================================

CONCEPT_PATTERNS: Dict[str, List[re.Pattern]] = {
    "ganancia_no_imponible": [
        re.compile(r"\bgananci(?:a|as)\s+no\s+imponible", re.I),
    ],
    "cargas_familia_conyuge": [
        re.compile(r"\bc[oó]nyuge\b", re.I),
    ],
    "cargas_familia_hijo": [
        re.compile(r"\bhijo\b(?!.*incapac)", re.I),
    ],
    "cargas_familia_hijo_incapaz": [
        re.compile(r"\bhijo.*incapac", re.I),
    ],
    "deduccion_especial_ap1": [
        re.compile(r"deducci[oó]n\s+especial.*apartado\s*1\b(?!.*nuev)", re.I),
    ],
    "deduccion_especial_ap1_nuevos": [
        re.compile(r"apartado\s*1.*nuev", re.I),
        re.compile(r"nuevos\s+profesionales", re.I),
    ],
    "deduccion_especial_ap2": [
        re.compile(r"deducci[oó]n\s+especial.*apartado\s*2\b", re.I),
    ],
}


# =============================================================================
# Limpieza inteligente de números
# =============================================================================

@dataclass
class CleaningResult:
    """Resultado de limpieza de un número."""
    value: Optional[float]
    raw: str
    steps: List[str]
    warnings: List[str]
    is_valid: bool = True


def clean_number_ar(
    raw_value: str,
    concepto: str,
    year: int,
    verbose: bool = False
) -> CleaningResult:
    """
    Limpia y parsea número argentino con detección de corrupción.
    
    Detecta y corrige:
    - Espacios mal colocados: "3 .503 .688,17"
    - Dígitos faltantes: ".299.771,52"
    - Separadores mal formateados
    
    Args:
        raw_value: Valor crudo del PDF
        concepto: Concepto para validación contextual
        year: Año para validación
        verbose: Logging detallado
    
    Returns:
        CleaningResult con valor, pasos aplicados y warnings
    """
    result = CleaningResult(
        value=None,
        raw=raw_value,
        steps=[],
        warnings=[]
    )
    
    log_debug(f"Limpiando '{raw_value}' para concepto '{concepto}'", verbose)
    
    # Detectar corrupción
    corruption_flags = []
    if ' ' in raw_value:
        corruption_flags.append("HAS_SPACES")
    if raw_value.startswith('.'):
        corruption_flags.append("STARTS_WITH_DOT")
    if '\n' in raw_value:
        corruption_flags.append("HAS_NEWLINE")
    
    if corruption_flags:
        result.warnings.append(f"Corruption: {', '.join(corruption_flags)}")
        log_debug(f"  Corruption flags: {corruption_flags}", verbose)
    
    # Limpiar
    cleaned = raw_value.strip()
    
    # Remover espacios
    if ' ' in cleaned:
        cleaned = cleaned.replace(' ', '')
        result.steps.append("REMOVED_SPACES")
        log_debug(f"  After removing spaces: '{cleaned}'", verbose)
    
    # Remover newlines
    if '\n' in cleaned:
        cleaned = cleaned.replace('\n', '')
        result.steps.append("REMOVED_NEWLINES")
    
    # Heurística: si empieza con punto y tiene 6 dígitos, prepend '3'
    if cleaned.startswith('.') and ',' in cleaned:
        parts = cleaned.split(',')
        digit_count = len(parts[0].replace('.', ''))
        
        if digit_count == 6:
            cleaned = '3' + cleaned
            result.steps.append("PREPENDED_3_HEURISTIC")
            result.warnings.append("Applied heuristic: prepended '3' for 6-digit pattern")
            log_debug(f"  Applied prepend heuristic: '{cleaned}'", verbose)
    
    # Validar separador decimal
    if ',' not in cleaned:
        result.warnings.append("No decimal separator found")
        log_error(f"No decimal separator in: {cleaned}")
        return result
    
    # Parsear
    try:
        parts = cleaned.split(',')
        integer_part = parts[0].replace('.', '')  # Remover separadores de miles
        decimal_part = parts[1][:2]  # Tomar solo 2 decimales
        
        value = float(f"{integer_part}.{decimal_part}")
        result.value = value
        result.steps.append("PARSED_SUCCESSFULLY")
        
        log_debug(f"  Parsed value: {value:,.2f}", verbose)
        
        # Validar contra rangos esperados
        if year in EXPECTED_RANGES and concepto in EXPECTED_RANGES[year]:
            min_val, max_val = EXPECTED_RANGES[year][concepto]
            if not (min_val <= value <= max_val):
                result.is_valid = False
                result.warnings.append(
                    f"Value {value:,.2f} outside expected range "
                    f"[{min_val:,.2f}, {max_val:,.2f}]"
                )
                log_warn(f"  Value outside expected range!")
        
    except (ValueError, IndexError) as e:
        result.warnings.append(f"Parse error: {e}")
        log_error(f"Failed to parse: {e}")
    
    return result


# =============================================================================
# Parser principal
# =============================================================================

class Art30Parser:
    """Parser para Artículo 30 - Deducciones Personales."""
    
    def __init__(self, year: int, verbose: bool = False):
        """
        Inicializa parser.
        
        Args:
            year: Año fiscal
            verbose: Logging detallado
        """
        self.year = year
        self.verbose = verbose
    
    def parse(
        self,
        pdf_path: Optional[Path] = None,
        pdf_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Parsea PDF de deducciones.
        
        Args:
            pdf_path: Ruta directa al PDF
            pdf_dir: Directorio con PDFs (busca por año)
        
        Returns:
            Dict con estructura:
            {
                'anio': int,
                'fuente': str,
                'items': {concepto: valor},
                'metadata': {...},
                'validation': {...}
            }
        """
        # Determinar PDF
        if not pdf_path:
            if not pdf_dir:
                raise ValueError("Debe proveer pdf_path o pdf_dir")
            pdf_path = pdf_dir / f"Deducciones-personales-art-30-liquidacion-anual-{self.year}.pdf"
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")
        
        log_info(f"Parseando PDF: {pdf_path.name}")
        
        # Extraer texto
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text()
        
        if not text:
            raise ValueError("No se pudo extraer texto del PDF")
        
        log_info(f"Texto extraído: {len(text)} caracteres")
        
        # Extraer números
        all_numbers = self._extract_all_numbers(text)
        log_info(f"Números encontrados: {len(all_numbers)}")
        
        # Parsear conceptos
        items = {}
        cleaning_metadata = {}
        validation_warnings = []
        
        for i, concepto in enumerate(CONCEPT_PATTERNS.keys()):
            if i < len(all_numbers):
                raw_value = all_numbers[i]
                log_debug(f"\nProcesando {concepto}: '{raw_value}'", self.verbose)
                
                # Limpiar y parsear
                result = clean_number_ar(
                    raw_value,
                    concepto,
                    self.year,
                    self.verbose
                )
                
                if result.value is not None:
                    items[concepto] = result.value
                    
                    # Guardar metadata de limpieza
                    cleaning_metadata[concepto] = {
                        "raw": result.raw,
                        "steps": result.steps,
                        "warnings": result.warnings,
                        "is_valid": result.is_valid
                    }
                    
                    if not result.is_valid:
                        validation_warnings.append(f"{concepto}: {result.warnings[-1]}")
                    
                    log_info(f"  {concepto}: {result.value:,.2f}")
                    if result.warnings:
                        for warn in result.warnings:
                            log_warn(f"    {warn}")
                else:
                    log_error(f"  {concepto}: Failed to parse")
        
        # Construir resultado
        return {
            "anio": self.year,
            "fuente": "ARCA",
            "items": items,
            "metadata": {
                "source_file": pdf_path.name,
                "parse_date": datetime.now().isoformat(),
                "parser_version": "2.0",
                "cleaning_details": cleaning_metadata
            },
            "validation": {
                "total_expected": len(CONCEPT_PATTERNS),
                "total_found": len(items),
                "warnings": validation_warnings
            },
            "missing": [c for c in CONCEPT_PATTERNS if c not in items],
            "extra_found": []  # Mantener compatibilidad
        }
    
    def _extract_all_numbers(self, text: str) -> List[str]:
        """Extrae todos los números del texto."""
        pattern = r'[\d\s\.]+,\d{1,2}'
        matches = re.findall(pattern, text)
        return [m.strip() for m in matches if m.strip()]


# =============================================================================
# CLI
# =============================================================================

def main():
    """Entry point para uso standalone."""
    parser = argparse.ArgumentParser(description="Parser Art. 30 v2.0")
    parser.add_argument("--year", type=int, required=True, help="Año fiscal")
    parser.add_argument("--pdf", type=str, help="Ruta al PDF")
    parser.add_argument("--pdf-dir", type=str, help="Directorio con PDFs")
    parser.add_argument("--out", type=str, help="Archivo de salida JSON")
    parser.add_argument("--verbose", action="store_true", help="Logging detallado")
    
    args = parser.parse_args()
    
    # Parsear
    pdf_path = Path(args.pdf) if args.pdf else None
    pdf_dir = Path(args.pdf_dir) if args.pdf_dir else None
    
    art30_parser = Art30Parser(year=args.year, verbose=args.verbose)
    data = art30_parser.parse(pdf_path=pdf_path, pdf_dir=pdf_dir)
    
    # Mostrar resumen
    log_info(f"Conceptos parseados: {len(data['items'])}")
    if data["missing"]:
        log_warn(f"Faltantes: {data['missing']}")
    if data["validation"]["warnings"]:
        log_warn("Validation warnings:")
        for warn in data["validation"]["warnings"]:
            log_warn(f"  {warn}")
    
    # Guardar
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        log_info(f"JSON guardado en: {out_path}")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()