#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LA IDEA DE ESTE SCRIPT ES AUDITAR EL REPOSITORIO PARA DETECTAR:
# - Archivos basura (logs, .pyc, Thumbs.db, .DS_Store, etc)
# - Archivos grandes que no deberían estar (pdf, zip, xlsx, etc)
# - Archivos duplicados (mismo contenido)
# - Resumen de tamaños por directorio y por extensión
    

import os
import re
import json
import hashlib
from pathlib import Path
from collections import defaultdict

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".idea", ".vscode"
}

JUNK_PATTERNS = [
    r".*\.pyc$",
    r".*\.pyo$",
    r".*\.log$",
    r".*Thumbs\.db$",
    r".*\.DS_Store$",
]

# Archivos grandes que suelen colarse
BIG_FILE_EXTS = {".pdf", ".zip", ".7z", ".rar", ".csv", ".xlsx", ".xlsm"}

def sha256_file(path: Path, chunk_size=1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def is_excluded_dir(p: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in p.parts)

def matches_any(patterns, s: str) -> bool:
    return any(re.match(p, s) for p in patterns)

def main():
    root = Path(".").resolve()
    files = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if is_excluded_dir(p.relative_to(root)):
            continue
        files.append(p)

    # 1) Tree summary + sizes
    total_size = 0
    by_dir_size = defaultdict(int)
    by_ext_size = defaultdict(int)

    # 2) Duplicates by hash
    hashes = defaultdict(list)

    # 3) Junk candidates
    junk = []

    # 4) Outputs/raw and outputs/normalized inventory
    raw_json = []
    normalized_json = []

    for p in files:
        try:
            sz = p.stat().st_size
        except OSError:
            continue

        total_size += sz
        rel = p.relative_to(root)
        by_dir_size[str(rel.parent)] += sz
        by_ext_size[p.suffix.lower()] += sz

        if matches_any(JUNK_PATTERNS, p.name):
            junk.append(str(rel))

        # index outputs
        if rel.parts[:2] == ("outputs", "raw") and p.suffix.lower() == ".json":
            raw_json.append(str(rel))
        if rel.parts[:2] == ("outputs", "normalized") and p.suffix.lower() == ".json":
            normalized_json.append(str(rel))

        # hashes for duplicates (solo para archivos "pequeños/medios" para no tardar infinito)
        # Si querés hash de TODO, saco este if.
        if sz <= 25 * 1024 * 1024:  # 25MB
            try:
                h = sha256_file(p)
                hashes[h].append(str(rel))
            except Exception:
                pass

    dups = {h: paths for h, paths in hashes.items() if len(paths) > 1}

    # 5) Big files report
    big_files = []
    for p in files:
        rel = p.relative_to(root)
        ext = p.suffix.lower()
        if ext in BIG_FILE_EXTS:
            try:
                big_files.append((str(rel), p.stat().st_size))
            except OSError:
                pass
    big_files.sort(key=lambda x: x[1], reverse=True)

    # 6) Quick “maybe unused” scripts
    # Heurística: archivos en normalizers/parsers que no son importados por nadie (muy aproximado)
    py_files = [p for p in files if p.suffix.lower() == ".py"]
    text_cache = {}
    for p in py_files:
        try:
            text_cache[str(p.relative_to(root))] = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text_cache[str(p.relative_to(root))] = ""

    imports_index = defaultdict(set)  # module_name -> {filepaths that import it}
    module_name_of = {}
    for relpath in text_cache.keys():
        # module name aproximado: ruta sin .py con / -> .
        module_name_of[relpath] = relpath[:-3].replace(os.sep, ".")
    import_re = re.compile(r"^\s*(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\.]+))", re.M)

    for relpath, txt in text_cache.items():
        for m in import_re.finditer(txt):
            mod = m.group(1) or m.group(2)
            if mod:
                imports_index[mod].add(relpath)

    maybe_unused = []
    for relpath, modname in module_name_of.items():
        # no marcar __init__.py
        if relpath.endswith("__init__.py"):
            continue
        # si nadie lo importa "por nombre exacto", lo ponemos como candidato (heurística)
        if modname not in imports_index:
            # pero excluimos entrypoints típicos
            if Path(relpath).name in {"normalize_all.py", "test_parsers.py"}:
                continue
            maybe_unused.append(relpath)

    report = {
        "root": str(root),
        "total_size_bytes": total_size,
        "top_dirs_by_size_bytes": sorted(by_dir_size.items(), key=lambda x: x[1], reverse=True)[:25],
        "top_exts_by_size_bytes": sorted(by_ext_size.items(), key=lambda x: x[1], reverse=True)[:25],
        "junk_candidates": sorted(junk),
        "duplicate_files_by_hash": dups,
        "big_files_top50": big_files[:50],
        "outputs_raw_json": sorted(raw_json),
        "outputs_normalized_json": sorted(normalized_json),
        "maybe_unused_py_heuristic": sorted(maybe_unused),
    }

    out_path = root / "audit_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Reporte generado: {out_path}")

if __name__ == "__main__":
    main()
