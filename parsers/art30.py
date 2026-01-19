"""
Parser mejorado para Art.30 con manejo robusto de diferentes formatos de PDF
y corrección inteligente de corrupción en números.

Maneja tres escenarios:
1. PDFs con tablas bien formadas (2025) -> extracción directa
2. PDFs sin tablas pero texto limpio (2023) -> regex en texto plano
3. PDFs con corrupción en números (2024) -> detección y corrección inteligente
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import pdfplumber

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

FILES_DIR = Path(r"C:\Users\franl\Desktop\impuestos\files")
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_KEYS = [
    "ganancia_no_imponible",
    "cargas_familia_conyuge",
    "cargas_familia_hijo",
    "cargas_familia_hijo_incapaz",
    "deduccion_especial_ap1",
    "deduccion_especial_ap1_nuevo",
    "deduccion_especial_ap2",
]

# Valores de referencia esperados por concepto (aproximados en millones)
# Esto ayuda a detectar si un valor está fuera de rango esperado
EXPECTED_RANGES = {
    "ganancia_no_imponible": (2_000_000, 5_000_000),
    "cargas_familia_conyuge": (2_000_000, 5_000_000),
    "cargas_familia_hijo": (1_000_000, 3_000_000),
    "cargas_familia_hijo_incapaz": (2_000_000, 5_000_000),
    "deduccion_especial_ap1": (8_000_000, 15_000_000),
    "deduccion_especial_ap1_nuevo": (10_000_000, 18_000_000),
    "deduccion_especial_ap2": (12_000_000, 20_000_000),
}

# ============================================================================
# FUNCIONES DE NORMALIZACIÓN Y DETECCIÓN
# ============================================================================

def _norm(s: str) -> str:
    """Normalizar texto: minúsculas, sin acentos, espacios simples"""
    if not s:
        return ""
    s = s.lower().replace("á", "a").replace("é", "e").replace("í", "i")
    s = s.replace("ó", "o").replace("ú", "u")
    return re.sub(r"\s+", " ", s).strip()


def _match_concept(text: str) -> Optional[str]:
    """
    Detectar qué concepto representa el texto dado.
    
    Orden importante: primero los más específicos, luego los más generales
    para evitar falsos positivos.
    """
    text = _norm(text)
    
    # Hijo incapaz (muy específico)
    if "hijo incapac" in text or "2.1" in text:
        return "cargas_familia_hijo_incapaz"
    
    # Apartado 1 nuevo (debe ir antes que Apartado 1 genérico)
    if ("apartado 1" in text or "apartado1" in text or "aparsado 1" in text):
        if ("nuevo" in text or "profesional" in text):
            return "deduccion_especial_ap1_nuevo"
    
    # Apartado 2
    if ("apartado 2" in text or "apartado2" in text or "aparsado 2" in text):
        return "deduccion_especial_ap2"
    
    # Apartado 1 genérico
    if ("apartado 1" in text or "apartado1" in text or "aparsado 1" in text):
        return "deduccion_especial_ap1"
    
    # Cónyuge
    if any(term in text for term in ["conyuge", "union convivencial", "1."]):
        return "cargas_familia_conyuge"
    
    # Hijo (pero no incapaz)
    if ("2. hijo" in text or "2 . hijo" in text or "2.hijo" in text):
        if "incapac" not in text:
            return "cargas_familia_hijo"
    
    # Ganancia no imponible
    if "ganancia" in text and "no imponible" in text:
        return "ganancia_no_imponible"
    
    return None


# ============================================================================
# FUNCIONES DE LIMPIEZA Y VALIDACIÓN DE MONTOS
# ============================================================================

def _detect_corruption(raw: str) -> Tuple[bool, str]:
    """
    Detectar si un número argentino tiene corrupción y tipo de corrupción.
    
    Returns:
        (is_corrupted, corruption_type)
    
    Tipos de corrupción detectados:
    - "missing_first_digit": Empieza con punto (ej: ".123.456,78")
    - "space_in_decimals": Espacios en la parte decimal (ej: "123.456,7 8")
    - "missing_digit_middle": Falta dígito en medio (ej: "1.23.456,78" debería ser "12.234.567,89")
    """
    if not raw:
        return False, "none"
    
    clean = raw.strip()
    
    # Patrón 1: Empieza con punto
    if clean.startswith("."):
        return True, "missing_first_digit"
    
    # Patrón 2: Tiene espacios en los decimales o puntos
    if " " in clean:
        return True, "space_in_decimals"
    
    # Patrón 3: Verificar estructura correcta
    # Un número argentino válido: d{1,3}(.d{3})*,d{2}
    if not re.match(r"^\d{1,3}(?:\.\d{3})*,\d{2}$", clean):
        return True, "invalid_format"
    
    return False, "none"


def _fix_corruption(raw: str, concept: Optional[str] = None) -> Optional[str]:
    """
    Intentar corregir números corruptos basándose en patrones conocidos
    y rangos esperados para cada concepto.
    
    Args:
        raw: String con el número (potencialmente corrupto)
        concept: El concepto al que pertenece (para validar rango)
    
    Returns:
        String corregido o None si no se pudo corregir
    """
    if not raw:
        return None
    
    clean = raw.strip().replace(" ", "")  # Eliminar espacios
    
    # PASO 1: Arreglar decimales incompletos (,6 -> ,60 o ,63)
    # Patrón: número seguido de coma y solo 1 dígito
    if re.match(r"^\.?[\d\.]+,\d$", clean):
        # Agregar un 0 al final
        clean = clean + "0"
    
    # PASO 2: Detectar corrupción
    is_corrupt, corruption_type = _detect_corruption(clean)
    
    if not is_corrupt:
        # Ya está limpio, solo validar formato
        if re.match(r"^\d{1,3}(?:\.\d{3})*,\d{2}$", clean):
            return clean
        return None
    
    # PASO 3: Corrección según tipo
    
    # CORRECCIÓN: Missing first digit
    if corruption_type == "missing_first_digit":
        # Caso especial: ".53.688,17" -> necesita convertirse a "3.503.688,17"
        # Este tipo de corrupción requiere análisis más profundo
        
        # Primero, intentar simplemente agregando dígito al inicio
        best_candidate = None
        best_score = 0
        
        for digit in range(1, 10):
            candidate = f"{digit}{clean}"
            
            # Verificar si el formato es válido
            if re.match(r"^\d{1,3}(?:\.\d{3})*,\d{2}$", candidate):
                # Calcular score basado en rango esperado
                if concept:
                    if _validate_against_range(candidate, concept):
                        # Este candidato está en rango
                        score = 100
                        if score > best_score:
                            best_score = score
                            best_candidate = candidate
                else:
                    # Sin concepto, devolver el primero válido
                    return candidate
        
        # Si encontramos un candidato en rango, devolverlo
        if best_candidate:
            return best_candidate
        
        # Si no funcionó, intentar corrección más agresiva para ".53.688,17"
        # Este caso necesita insertar el dígito en otra posición
        if "." in clean and clean.startswith(".") and clean.count(".") == 2:
            # Formato: ".XX.XXX,XX" -> debería ser "X.XXX.XXX,XX"
            # Extraer las partes
            parts = clean[1:].split(".")  # Remover primer punto y split
            if len(parts) == 2:
                part1, rest = parts
                # Probar insertando dígitos
                for digit in range(1, 10):
                    # Formato correcto: X.XXX.XXX,XX
                    if len(part1) == 2:  # "53" en ".53.688,17"
                        candidate = f"{digit}.{digit}{part1}.{rest}"
                        if re.match(r"^\d{1,3}(?:\.\d{3})*,\d{2}$", candidate):
                            if concept and _validate_against_range(candidate, concept):
                                return candidate
        
        return None
    
    # CORRECCIÓN: Spaces in decimals
    if corruption_type == "space_in_decimals":
        # Ya removimos espacios al inicio
        if re.match(r"^\d{1,3}(?:\.\d{3})*,\d{2}$", clean):
            return clean
        return None
    
    # Si no pudimos corregir, retornar None
    return None


def _validate_against_range(amount_str: str, concept: str) -> bool:
    """
    Validar si un monto está dentro del rango esperado para un concepto.
    
    Útil para descartar correcciones incorrectas.
    """
    if concept not in EXPECTED_RANGES:
        return True  # Si no tenemos rango, aceptar
    
    try:
        # Convertir formato argentino a float
        amount_float = float(amount_str.replace(".", "").replace(",", "."))
        min_val, max_val = EXPECTED_RANGES[concept]
        return min_val <= amount_float <= max_val
    except:
        return False


def _clean_amount(raw: str, concept: Optional[str] = None) -> Optional[str]:
    """
    Limpiar, validar y posiblemente corregir un monto en formato argentino.
    
    Args:
        raw: String con el monto
        concept: Concepto al que pertenece (opcional, para validación)
    
    Returns:
        String limpio y validado, o None si no es válido
    """
    if not raw:
        return None
    
    # Intentar corrección si está corrupto
    fixed = _fix_corruption(raw, concept)
    
    if fixed:
        return fixed
    
    # Si no hubo corrupción o no se pudo corregir, validar formato normal
    clean = raw.replace(" ", "").strip()
    if re.match(r"^\d{1,3}(?:\.\d{3})*,\d{2}$", clean):
        # Opcional: validar contra rango
        if concept and not _validate_against_range(clean, concept):
            return None
        return clean
    
    return None


# ============================================================================
# FUNCIONES DE EXTRACCIÓN
# ============================================================================

def _extract_from_table(table: List[List[str]], assignments: Dict[str, str]) -> None:
    """
    Extraer conceptos y valores de una tabla.
    
    Args:
        table: Lista de filas, cada fila es una lista de celdas
        assignments: Diccionario donde se guardan los resultados
    """
    for row in table:
        if not row or len(row) < 2:
            continue
        
        concepto_cell = row[0] or ""
        valor_cell = row[1] or ""
        
        concept = _match_concept(concepto_cell)
        if concept:
            amount = _clean_amount(valor_cell, concept)
            if amount:
                assignments[concept] = amount


def _extract_from_text(text: str, assignments: Dict[str, str]) -> None:
    """
    Extraer conceptos y valores del texto plano.
    
    Busca línea por línea:
    1. Identificar el concepto
    2. Buscar el valor (puede estar en la misma línea o en la siguiente)
    
    Args:
        text: Texto completo de la página
        assignments: Diccionario donde se guardan los resultados
    """
    lines = text.split("\n")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        concept = _match_concept(line)
        if not concept:
            continue
        
        # Buscar números en esta línea (incluyendo corruptos que empiezan con punto)
        # Patrón: captura números normales O números que empiezan con punto
        amounts = re.findall(r"\.?[\d\.\s]+,[\d\s]+", line)
        
        # Si no hay números en esta línea, buscar en la siguiente
        if not amounts and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            amounts = re.findall(r"\.?[\d\.\s]+,[\d\s]+", next_line)
        
        # Procesar todos los montos encontrados
        for raw_amount in amounts:
            # Limpiar y corregir si es necesario
            amount = _clean_amount(raw_amount, concept)
            
            if amount:
                # Evitar sobreescribir con valores de tablas de acumulados mensuales
                # (esos son valores más chicos que los anuales)
                if concept not in assignments:
                    assignments[concept] = amount
                else:
                    # Si ya existe, quedarse con el mayor (anual vs mensual)
                    existing_val = float(assignments[concept].replace(".", "").replace(",", "."))
                    new_val = float(amount.replace(".", "").replace(",", "."))
                    if new_val > existing_val:
                        assignments[concept] = amount
                
                break  # Solo tomar el primer monto válido por concepto


# ============================================================================
# FUNCIÓN PRINCIPAL DE PARSING
# ============================================================================

def parse(year: int) -> Dict:
    """
    Parsear el PDF del Art.30 para un año dado.
    
    Estrategia multi-capa:
    1. Intentar extracción de tablas (funciona en PDFs bien formados)
    2. Fallback a extracción de texto plano con corrección inteligente
    3. Validación final de completitud
    
    Args:
        year: Año fiscal (ej: 2024)
    
    Returns:
        Dict con metadata y los 7 valores esperados
    
    Raises:
        FileNotFoundError: Si el PDF no existe
    """
    pdf_name = f"Deducciones-personales-art-30-liquidacion-anual-{year}.pdf"
    pdf_path = FILES_DIR / pdf_name
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"No encontrado: {pdf_path}")
    
    assignments = {}
    
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            # ESTRATEGIA 1: Extraer de tablas
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    _extract_from_table(table, assignments)
            
            # ESTRATEGIA 2: Extraer de texto plano
            text = page.extract_text() or ""
            if text:
                _extract_from_text(text, assignments)
    
    # Construir resultado final con valores por defecto
    final_items = {}
    for key in EXPECTED_KEYS:
        final_items[key] = assignments.get(key, "0,00")
    
    # Metadata del resultado
    payload = {
        "anio": year,
        "fuente": "ARCA",
        "origen": "PDF_ART_30",
        "archivo": pdf_name,
        "items": final_items,
    }
    
    # Guardar JSON
    json_path = RAW_DIR / f"raw_art30_{year}.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    # Logging
    found = len([v for v in final_items.values() if v != '0,00'])
    print(f"✅ Art.30 {year}: {found}/{len(EXPECTED_KEYS)} encontrados")
    
    return payload


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    result = parse(year)
    
    # Mostrar resultado detallado
    print(f"\nResultado para {year}:")
    print(json.dumps(result, ensure_ascii=False, indent=2))