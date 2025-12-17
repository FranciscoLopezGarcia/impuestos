import json
from pathlib import Path

SITE_MAP = Path("outputs/site_map.json")
OUTPUT = Path("outputs/fuentes_utiles.txt")

with SITE_MAP.open(encoding="utf-8") as f:
    data = json.load(f)

lines = []

def add(title, url, tipo, aporta):
    lines.append(f"FUENTE: {title}")
    lines.append(f"URL: {url}")
    lines.append(f"TIPO: {tipo}")
    lines.append("DATOS QUE APORTA:")
    for a in aporta:
        lines.append(f"- {a}")
    lines.append("-" * 60)

for entry in data:
    url = entry.get("url", "")
    tipo = entry.get("type")

    # ===============================
    # DEDUCCIONES PERSONALES
    # ===============================
    if tipo == "pdf" and "deducciones" in url.lower() and "art-30" in url.lower():
        add(
            title=url.split("/")[-1],
            url=url,
            tipo="PDF (Deducciones personales)",
            aporta=[
                "Ganancia no imponible",
                "Cargas de familia (cónyuge, hijos)",
                "Deducción especial",
                "Topes (sepelio, seguros, servicio doméstico)",
            ],
        )

    # ===============================
    # ESCALAS GANANCIAS
    # ===============================
    elif tipo == "pdf" and "art-94" in url.lower():
        add(
            title=url.split("/")[-1],
            url=url,
            tipo="PDF (Escalas Ganancias)",
            aporta=[
                "Rangos de ganancia neta",
                "Monto fijo",
                "Porcentaje sobre excedente",
            ],
        )

    # ===============================
    # BIENES PERSONALES (HTML)
    # ===============================
    elif (
        tipo == "html"
        and "bienes-personales" in url.lower()
        and entry.get("tables")
    ):
        add(
            title=entry.get("title", "(sin título)"),
            url=url,
            tipo="HTML (Bienes Personales)",
            aporta=[
                "Escalas",
                "Alícuotas",
                "Diferencia Argentina / Exterior",
            ],
        )

OUTPUT.write_text("\n".join(lines), encoding="utf-8")

print("Resumen de fuentes generado:")
print(OUTPUT)
