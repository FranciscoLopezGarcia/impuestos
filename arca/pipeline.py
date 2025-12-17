# arca/pipeline.py

from arca.sources import fuentes_oficiales
from arca.mapper.crawler_dirigido import run as run_crawler

def collect_sources(year: int):
    """
    Devuelve TODAS las fuentes a usar en el pipeline.
    """

    fuentes = fuentes_oficiales(year)

    # Para HTML dinámico seguimos usando crawler (por si cambian paths)
    run_crawler()

    return fuentes
