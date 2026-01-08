"""
Common utilities for ARCA parsers.

Provides shared functionality across different parser modules including:
- Number cleaning and normalization
- Text processing
- Validation helpers
"""

import re
from typing import Tuple, List, Optional


def clean_number_string(
    raw: str,
    allow_spaces: bool = True,
    allow_multiple_dots: bool = True
) -> str:
    """
    Basic cleaning of number string.
    
    Args:
        raw: Raw number string
        allow_spaces: Remove spaces if True
        allow_multiple_dots: Keep dots if True (thousand separators)
    
    Returns:
        Cleaned string
    """
    cleaned = raw.strip()
    
    if allow_spaces:
        cleaned = cleaned.replace(' ', '')
    
    return cleaned


def extract_numbers_from_text(text: str) -> List[str]:
    """
    Extract all numbers from text using regex.
    
    Matches patterns like:
    - 123.456,78
    - 1.234.567,89
    - .53 .688,17 (corrupted)
    - 16.817.73 ,2 (corrupted with space before comma)
    
    Args:
        text: Text to extract numbers from
    
    Returns:
        List of number strings
    """
    # Pattern matches: optional digits, dots, spaces, comma, and decimal digits
    pattern = r'[\d\s\.]+,\d{1,2}'
    matches = re.findall(pattern, text)
    return [m.strip() for m in matches if m.strip()]


def format_number_for_json(value: float, decimals: int = 2) -> float:
    """
    Format number for JSON output.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
    
    Returns:
        Rounded float
    """
    return round(value, decimals)


def calculate_range(
    value: float,
    tolerance_percent: float = 20.0
) -> Tuple[float, float]:
    """
    Calculate validation range for a value.
    
    Args:
        value: Base value
        tolerance_percent: Tolerance percentage (default 20%)
    
    Returns:
        (min_value, max_value) tuple
    """
    tolerance = value * (tolerance_percent / 100.0)
    return (value - tolerance, value + tolerance)


def is_value_in_range(
    value: float,
    expected: float,
    tolerance_percent: float = 20.0
) -> bool:
    """
    Check if value is within expected range.
    
    Args:
        value: Value to check
        expected: Expected value
        tolerance_percent: Tolerance percentage
    
    Returns:
        True if value is within range
    """
    min_val, max_val = calculate_range(expected, tolerance_percent)
    return min_val <= value <= max_val