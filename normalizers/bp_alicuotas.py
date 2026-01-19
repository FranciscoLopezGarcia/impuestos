import json
from pathlib import Path
from utils import to_number

import sys
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"

# Archivo con todas las tablas completas
RAW_ALL = RAW_DIR / "raw_bienes_alicuotas_all.json"


def _extract_tramos_from_table(rows):

    tramos = []
    for r in rows:
        if not isinstance(r, list) or len(r) < 4:
            continue

        # Esperamos filas tipo: [desde, hasta, pagaran, porcentaje, excedente]
        if len(r) >= 5:
            desde, hasta, pagaran, porc, exced = r[0], r[1], r[2], r[3], r[4]
        else:
            continue

        # Descartamos headers
        if "más de" in str(desde).lower() or "valor total" in str(desde).lower():
            continue

        # Al menos debe tener porcentaje tipo "0,50%"
        if "%" not in str(porc):
            continue

        tramos.append({
            "desde": desde,
            "hasta": hasta,
            "pagaran": pagaran,
            "porcentaje": porc,
            "excedente_desde": exced,
        })
    
    return tramos


def normalize_bp_alicuotas(year_filter=None):
   
    # Verificar si existe el archivo completo
    if not RAW_ALL.exists():
        print(f"⚠️  No se encuentra {RAW_ALL}")
        return []
    
    # Cargar archivo completo con todas las tablas
    try:
        data_all = json.loads(RAW_ALL.read_text(encoding="utf-8"))
        tablas_completas = data_all.get("tablas", [])
    except Exception as e:
        print(f"⚠️  Error leyendo {RAW_ALL.name}: {e}")
        return []
    
    out = []
    
    # Si hay filtro de año, buscar solo ese archivo
    if year_filter:
        years_to_process = [year_filter]
    else:
        # Sin filtro, buscar todos los archivos disponibles
        pattern = "raw_bienes_alicuotas_*.json"
        files = sorted(RAW_DIR.glob(pattern))
        years_to_process = []
        for f in files:
            # Saltar el archivo _all
            if f.name == "raw_bienes_alicuotas_all.json":
                continue
            # Extraer año del nombre: raw_bienes_alicuotas_2024.json -> 2024
            try:
                year = int(f.stem.split('_')[-1])
                years_to_process.append(year)
            except ValueError:
                continue
    
    # Procesar cada año
    for year in sorted(years_to_process):
        raw_file = RAW_DIR / f"raw_bienes_alicuotas_{year}.json"
        
        if not raw_file.exists():
            continue
        
        try:
            data_year = json.loads(raw_file.read_text(encoding="utf-8"))
            alicuotas = data_year.get("alicuotas", {})
            
            # Procesar tabla "pais" (GENERAL)
            if "pais" in alicuotas:
                indices_general = alicuotas["pais"].get("rows", [])
                for idx in indices_general:
                    # Buscar la tabla con ese índice
                    tabla = next((t for t in tablas_completas if t.get("index") == idx), None)
                    if not tabla:
                        continue
                    
                    rows = tabla.get("rows", [])
                    tramos = _extract_tramos_from_table(rows)
                    
                    for i, t in enumerate(tramos, start=1):
                        out.append({
                            "concepto": f"BP_ALICUOTA_GENERAL_TRAMO_{i}",
                            "impuesto": "BIENES_PERSONALES",
                            "anio": year,
                            "desde": to_number(t["desde"]),
                            "hasta": to_number(t["hasta"]),
                            "monto_fijo": to_number(t["pagaran"]),
                            "porcentaje": to_number(t["porcentaje"]),
                            "excedente_desde": to_number(t["excedente_desde"]),
                            "unidad": "ARS/%",
                            "fuente": data_year.get("fuente", "ARCA"),
                            "origen": "HTML_ALICUOTAS",
                            "url": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/conceptos-basicos/alicuotas.asp",
                        })
            
            # Procesar tabla "exterior" (CUMPLIDORES)
            if "exterior" in alicuotas:
                indices_cumpl = alicuotas["exterior"].get("rows", [])
                for idx in indices_cumpl:
                    # Buscar la tabla con ese índice
                    tabla = next((t for t in tablas_completas if t.get("index") == idx), None)
                    if not tabla:
                        continue
                    
                    rows = tabla.get("rows", [])
                    tramos = _extract_tramos_from_table(rows)
                    
                    for i, t in enumerate(tramos, start=1):
                        out.append({
                            "concepto": f"BP_ALICUOTA_CUMPLIDORES_TRAMO_{i}",
                            "impuesto": "BIENES_PERSONALES",
                            "anio": year,
                            "desde": to_number(t["desde"]),
                            "hasta": to_number(t["hasta"]),
                            "monto_fijo": to_number(t["pagaran"]),
                            "porcentaje": to_number(t["porcentaje"]),
                            "excedente_desde": to_number(t["excedente_desde"]),
                            "unidad": "ARS/%",
                            "fuente": data_year.get("fuente", "ARCA"),
                            "origen": "HTML_ALICUOTAS",
                            "url": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/conceptos-basicos/alicuotas.asp",
                        })
        
        except Exception as e:
            print(f"⚠️  Error procesando {raw_file.name}: {e}")
            continue
    
    return out