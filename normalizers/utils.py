import re

def to_number(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)

    s = str(x).strip()

    # porcentaje
    if s.endswith("%"):
        s = s.replace("%", "").strip()
        return to_number(s)

    # limpiar moneda y separadores
    s = s.replace("$", "").replace(" ", "")
    s = s.replace(".", "")          # miles
    s = s.replace(",", ".")         # decimal

    # caso "en adelante"
    if "adelante" in s.lower():
        return None

    # solo números
    if not re.search(r"\d", s):
        return None

    try:
        return float(s)
    except:
        return None