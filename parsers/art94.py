# parsers/art94.py - VERSIÓN MEJORADA
import pdfplumber
import json
from pathlib import Path
import sys
import re


BASE_DIR = Path(__file__).resolve().parents[1]
FILES_DIR = Path(r"C:\Users\franl\Desktop\impuestos\files")
RAW_DIR = BASE_DIR / "outputs" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# Valores oficiales ARCA 2024 (fallback)
# =========================

ESCALAS_OFICIALES_2024 = [
    {"desde": "0,00", "hasta": "1.360.200,00", "monto_fijo": "0,00", "porcentaje": "5", "excedente_desde": "0,00"},
    {"desde": "1.360.200,00", "hasta": "2.720.400,00", "monto_fijo": "68.010,00", "porcentaje": "9", "excedente_desde": "1.360.200,00"},
    {"desde": "2.720.400,00", "hasta": "4.080.600,00", "monto_fijo": "190.428,00", "porcentaje": "12", "excedente_desde": "2.720.400,00"},
    {"desde": "4.080.600,00", "hasta": "6.120.900,00", "monto_fijo": "353.652,00", "porcentaje": "15", "excedente_desde": "4.080.600,00"},
    {"desde": "6.120.900,00", "hasta": "12.241.800,00", "monto_fijo": "659.697,00", "porcentaje": "19", "excedente_desde": "6.120.900,00"},
    {"desde": "12.241.800,00", "hasta": "18.362.700,00", "monto_fijo": "1.822.668,00", "porcentaje": "23", "excedente_desde": "12.241.800,00"},
    {"desde": "18.362.700,00", "hasta": "27.544.050,00", "monto_fijo": "3.230.475,00", "porcentaje": "27", "excedente_desde": "18.362.700,00"},
    {"desde": "27.544.050,00", "hasta": "41.316.075,00", "monto_fijo": "5.709.439,50", "porcentaje": "31", "excedente_desde": "27.544.050,00"},
    {"desde": "41.316.075,00", "hasta": "en adelante", "monto_fijo": "9.978.767,25", "porcentaje": "35", "excedente_desde": "41.316.075,00"},
]

# Porcentajes estándar (siempre son estos)
PORCENTAJES_ESTANDAR = ["5", "9", "12", "15", "19", "23", "27", "31", "35"]


def clean_number(raw: str) -> str:
    """Limpia números argentinos"""
    if not raw or not isinstance(raw, str):
        return ""
    
    cleaned = raw.replace(" ", "").strip()
    
    # Normalizar puntos múltiples
    cleaned = re.sub(r"\.{2,}", ".", cleaned)
    
    if "," in cleaned:
        partes = cleaned.split(",", 1)
        antes = partes[0]
        despues = partes[1] if len(partes) > 1 else "00"
        
        dig_ent = "".join(re.findall(r"\d", antes))
        dig_dec = "".join(re.findall(r"\d", despues))
        
        # Completar decimales
        if len(dig_dec) < 2:
            dig_dec = dig_dec.ljust(2, "0")
        else:
            dig_dec = dig_dec[:2]
        
        # Formatear enteros con puntos de miles
        if len(dig_ent) >= 1:
            res = []
            for i, d in enumerate(reversed(dig_ent)):
                if i > 0 and i % 3 == 0:
                    res.append(".")
                res.append(d)
            cleaned = "".join(reversed(res)) + "," + dig_dec
    
    return cleaned


def parse(year: int = None):
    """Parser mejorado para Art.94"""
    
    if year is None:
        year = 2024
    
    # Buscar PDF con múltiples patrones
    posibles = [
        f"Tabla-art-94-liquidacion-anual-final-{year}.pdf",
        f"Escalas-del-Art-94-de-la-Ley-del-Impuesto-a-las-Ganancias-periodo-{year}.pdf",
    ]
    
    pdf_path = None
    for nombre in posibles:
        candidato = FILES_DIR / nombre
        if candidato.exists():
            pdf_path = candidato
            break
    
    if not pdf_path:
        raise FileNotFoundError(f"No se encontró PDF Art.94 para {year}")
    
    out_path = RAW_DIR / f"raw_art94_{year}.json"
    
    print(f"📄 Parseando Art. 94 {year}: {pdf_path.name}")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            texto = page.extract_text() or ""
            lineas = [l.strip() for l in texto.split("\n") if l.strip()]
            
            # Extraer escalas raw
            escalas_raw = []
            
            i = 0
            while i < len(lineas):
                linea = lineas[i]
                
                # Buscar números argentinos en la línea
                numeros_raw = re.findall(r"[\d\.\s]+,\d{2}", linea)
                
                if len(numeros_raw) >= 2:
                    # Limpiar números
                    numeros = [clean_number(n) for n in numeros_raw]
                    numeros = [n for n in numeros if n and len(n) > 3]
                    
                    # Buscar porcentaje en la línea
                    porcentaje = None
                    
                    # Método 1: Al final de la línea
                    match = re.search(r'\b(\d{1,2})\s*$', linea)
                    if match:
                        pct = match.group(1)
                        if int(pct) <= 35:
                            porcentaje = pct
                    
                    # Método 2: Línea siguiente
                    if not porcentaje and i + 1 < len(lineas):
                        siguiente = lineas[i + 1].strip()
                        if siguiente.isdigit() and len(siguiente) <= 2:
                            pct_val = int(siguiente)
                            if 5 <= pct_val <= 35:
                                porcentaje = siguiente
                                i += 1  # Skip siguiente línea
                    
                    if numeros:
                        escalas_raw.append({
                            "numeros": numeros,
                            "porcentaje": porcentaje,
                            "linea": linea
                        })
                
                i += 1
            
            print(f"   ✓ Filas parseadas: {len(escalas_raw)}")
            
            # Construir escalas finales
            escalas = []
            
            for idx, row in enumerate(escalas_raw):
                nums = row["numeros"]
                pct = row["porcentaje"]
                
                # Asignar porcentaje estándar si falta
                if not pct and idx < len(PORCENTAJES_ESTANDAR):
                    pct = PORCENTAJES_ESTANDAR[idx]
                
                # Última escala (en adelante)
                es_ultima = (idx == len(escalas_raw) - 1)
                
                if es_ultima:
                    # Última escala: desde, hasta="en adelante", monto_fijo, porcentaje
                    escalas.append({
                        "desde": nums[0] if len(nums) > 0 else "0,00",
                        "hasta": "en adelante",
                        "monto_fijo": nums[1] if len(nums) > 1 else "0,00",
                        "porcentaje": pct or "35",
                        "excedente_desde": nums[0] if len(nums) > 0 else "0,00"
                    })
                
                elif len(nums) == 2:
                    # Primera escala: desde, hasta (sin monto_fijo)
                    escalas.append({
                        "desde": nums[0],
                        "hasta": nums[1],
                        "monto_fijo": "0,00",
                        "porcentaje": pct or "5",
                        "excedente_desde": nums[0]
                    })
                
                elif len(nums) >= 4:
                    # Escalas intermedias: desde, hasta, monto_fijo, excedente_desde
                    escalas.append({
                        "desde": nums[0],
                        "hasta": nums[1],
                        "monto_fijo": nums[2],
                        "porcentaje": pct or PORCENTAJES_ESTANDAR[idx],
                        "excedente_desde": nums[3] if len(nums) > 3 else nums[0]
                    })
                
                elif len(nums) == 3:
                    # 3 números: desde, hasta, monto_fijo
                    escalas.append({
                        "desde": nums[0],
                        "hasta": nums[1],
                        "monto_fijo": nums[2],
                        "porcentaje": pct or PORCENTAJES_ESTANDAR[idx],
                        "excedente_desde": nums[0]
                    })
            
            print(f"   ✓ Escalas construidas: {len(escalas)}")
            
            # Validar cantidad
            if len(escalas) != 9:
                print(f"   ⚠ Extracción incompleta ({len(escalas)}/9)")
                
                # Para 2024, usar valores oficiales
                if year == 2024:
                    print(f"   → Usando valores oficiales ARCA 2024")
                    escalas = ESCALAS_OFICIALES_2024
                else:
                    print(f"   → Usando escalas extraídas (puede tener errores)")
    
    except Exception as e:
        print(f"   ❌ Error en extracción: {e}")
        
        if year == 2024:
            print(f"   → Usando valores oficiales ARCA 2024")
            escalas = ESCALAS_OFICIALES_2024
        else:
            raise
    
    # Guardar
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(escalas, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    print(f"\n✅ JSON guardado: {out_path}")
    print(f"   Total escalas: {len(escalas)}")
    
    return escalas


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    result = parse(year)
    
    print("\n" + "="*70)
    print("ESCALAS FINALES:")
    print("="*70)
    for i, e in enumerate(result, 1):
        print(f"{i}. {e['desde']:15} → {e['hasta']:15} | ${e['monto_fijo']:12} + {e['porcentaje']:2}%")