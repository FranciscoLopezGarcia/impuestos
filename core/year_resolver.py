import re
from pathlib import Path

YEAR_RE = re.compile(r"(19|20)\d{2}")

def resolve_year_from_path(path: Path):
    # 1️⃣ desde carpeta
    for p in path.parents:
        m = YEAR_RE.search(p.name)
        if m:
            return int(m.group())

    # 2️⃣ desde nombre de archivo
    m = YEAR_RE.search(path.name)
    if m:
        return int(m.group())

    return None
