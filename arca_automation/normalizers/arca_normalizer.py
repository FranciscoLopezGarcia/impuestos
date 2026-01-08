"""
Normalizador ARCA - Convierte datos crudos de parsers a formato Excel.

Formato de salida (coincide con estructura Excel):
{
    "concepto": "BP_MINIMO_NO_IMPONIBLE",
    "impuesto": "BIENES_PERSONALES",
    "anio": 2024,
    "valor": 292994964.89,  # para valores simples
    "desde": ...,           # para escalas/alícuotas
    "hasta": ...,
    "monto_fijo": ...,
    "porcentaje": ...,
    "excedente_desde": ...,
    "unidad": "ARS",
    "fuente": "ARCA",
    "origen": "HTML_DETERMINATIVA"
}
"""
from typing import Dict, List
from utils.logger import get_logger


class ARCANormalizer:
    """Normaliza datos de parsers a formato Excel."""
    
    def __init__(self, year: int):
        self.year = year
        self.logger = get_logger(self.__class__.__name__)
    
    def normalize_deducciones(self, raw: Dict) -> List[Dict]:
        """
        Normaliza deducciones personales (Art. 30).
        
        Args:
            raw: Dict con 'anio', 'fuente', 'items'
        
        Returns:
            Lista de registros normalizados
        """
        if not raw or 'items' not in raw:
            return []
        
        result = []
        items = raw['items']
        
        for key, valor_raw in items.items():
            result.append({
                "concepto": f"GAN_DED_{key.upper()}",
                "impuesto": "GANANCIAS",
                "anio": self.year,
                "valor": self._to_number(valor_raw),
                "desde": None,
                "hasta": None,
                "monto_fijo": None,
                "porcentaje": None,
                "excedente_desde": None,
                "unidad": "ARS",
                "fuente": "ARCA",
                "origen": "PDF_ART_30",
            })
        
        self.logger.debug(f"Deducciones normalizadas: {len(result)}")
        return result
    
    def normalize_escalas(self, raw: List[Dict]) -> List[Dict]:
        """
        Normaliza escalas de Ganancias (Art. 94).
        
        Args:
            raw: Lista de tramos con desde/hasta/monto_fijo/porcentaje/excedente_desde
        
        Returns:
            Lista de registros normalizados
        """
        if not raw:
            return []
        
        result = []
        
        for i, tramo in enumerate(raw, start=1):
            result.append({
                "concepto": f"GAN_ESCALA_TRAMO_{i}",
                "impuesto": "GANANCIAS",
                "anio": self.year,
                "valor": None,
                "desde": self._to_number(tramo.get("desde")),
                "hasta": self._to_number(tramo.get("hasta")),
                "monto_fijo": self._to_number(tramo.get("monto_fijo")),
                "porcentaje": self._to_number(tramo.get("porcentaje")),
                "excedente_desde": self._to_number(tramo.get("excedente_desde")),
                "unidad": "ARS/%",
                "fuente": "ARCA",
                "origen": "PDF_ART_94",
            })
        
        self.logger.debug(f"Escalas normalizadas: {len(result)}")
        return result
    
    def normalize_bp_alicuotas(self, raw: Dict) -> List[Dict]:
        """
        Normaliza alícuotas de Bienes Personales.
        
        Args:
            raw: Dict con 'tablas' (lista de tablas HTML)
        
        Returns:
            Lista de registros normalizados
        """
        if not raw or 'tablas' not in raw:
            return []
        
        tablas = raw['tablas']
        if not tablas:
            return []
        
        result = []
        
        # Detectar tabla general (score más alto)
        def table_score(tab):
            rows = tab.get("rows", [])
            tramos = self._extract_tramos_from_table(rows)
            if not tramos:
                return 0
            
            first_hasta = str(tramos[0].get("hasta", ""))
            # Tabla 2024 tiene "40.107.213,86" en primer hasta
            return 10 if "40.107.213,86" in first_hasta or "40.107.213" in first_hasta else 1
        
        tablas_sorted = sorted(tablas, key=table_score, reverse=True)
        
        # Tabla general
        general = tablas_sorted[0]
        tramos_general = self._extract_tramos_from_table(general.get("rows", []))
        
        for i, t in enumerate(tramos_general, start=1):
            result.append({
                "concepto": f"BP_ALICUOTA_GENERAL_TRAMO_{i}",
                "impuesto": "BIENES_PERSONALES",
                "anio": self.year,
                "valor": None,
                "desde": self._to_number(t.get("desde")),
                "hasta": self._to_number(t.get("hasta")),
                "monto_fijo": self._to_number(t.get("pagaran")),
                "porcentaje": self._to_number(t.get("porcentaje")),
                "excedente_desde": self._to_number(t.get("excedente_desde")),
                "unidad": "ARS/%",
                "fuente": "ARCA",
                "origen": "HTML_ALICUOTAS",
            })
        
        # Tabla cumplidores (si existe)
        if len(tablas_sorted) > 1:
            cumpl = tablas_sorted[1]
            tramos_cumpl = self._extract_tramos_from_table(cumpl.get("rows", []))
            
            for i, t in enumerate(tramos_cumpl, start=1):
                result.append({
                    "concepto": f"BP_ALICUOTA_CUMPLIDORES_TRAMO_{i}",
                    "impuesto": "BIENES_PERSONALES",
                    "anio": self.year,
                    "valor": None,
                    "desde": self._to_number(t.get("desde")),
                    "hasta": self._to_number(t.get("hasta")),
                    "monto_fijo": self._to_number(t.get("pagaran")),
                    "porcentaje": self._to_number(t.get("porcentaje")),
                    "excedente_desde": self._to_number(t.get("excedente_desde")),
                    "unidad": "ARS/%",
                    "fuente": "ARCA",
                    "origen": "HTML_ALICUOTAS",
                })
        
        self.logger.debug(f"Alícuotas BP normalizadas: {len(result)}")
        return result
    
    def normalize_bp_minimo(self, raw: Dict) -> List[Dict]:
        """
        Normaliza mínimo no imponible de BP.
        
        Args:
            raw: Dict con 'thresholds' (lista de umbrales por año)
        
        Returns:
            Lista con 1 registro (el del año actual)
        """
        if not raw or 'thresholds' not in raw:
            return []
        
        thresholds = raw['thresholds']
        if not thresholds:
            return []
        
        # Buscar el threshold del año actual
        latest = None
        for t in thresholds:
            if t.get('year') == self.year:
                latest = t
                break
        
        if not latest:
            # Fallback: usar el más reciente
            latest = max(thresholds, key=lambda x: x.get('year', 0))
        
        return [{
            "concepto": "BP_MINIMO_NO_IMPONIBLE",
            "impuesto": "BIENES_PERSONALES",
            "anio": latest.get('year'),
            "valor": self._to_number(latest.get('amount_raw')),
            "desde": None,
            "hasta": None,
            "monto_fijo": None,
            "porcentaje": None,
            "excedente_desde": None,
            "unidad": "ARS",
            "fuente": "ARCA",
            "origen": "HTML_DETERMINATIVA",
        }]
    
    def normalize_monedas(self, raw: Dict) -> List[Dict]:
        """
        Normaliza cotización de monedas.
        
        Args:
            raw: Dict con 'divisas' y 'billetes'
        
        Returns:
            Lista de registros (dólar billete y divisa, comp/vend)
        """
        if not raw:
            return []
        
        result = []
        
        # Buscar dólar en billetes
        billetes = raw.get('billetes', [])
        dolar_billete = self._find_dolar(billetes)
        
        if dolar_billete:
            result.append({
                "concepto": "BP_DOLAR_BILLETE_COMP_31_12",
                "impuesto": "BIENES_PERSONALES",
                "anio": self.year,
                "valor": self._to_number(dolar_billete.get('comprador')),
                "desde": None,
                "hasta": None,
                "monto_fijo": None,
                "porcentaje": None,
                "excedente_desde": None,
                "unidad": "ARS",
                "fuente": "ARCA",
                "origen": "PDF_MONEDA_EXTRANJERA",
            })
            
            result.append({
                "concepto": "BP_DOLAR_BILLETE_VEND_31_12",
                "impuesto": "BIENES_PERSONALES",
                "anio": self.year,
                "valor": self._to_number(dolar_billete.get('vendedor')),
                "desde": None,
                "hasta": None,
                "monto_fijo": None,
                "porcentaje": None,
                "excedente_desde": None,
                "unidad": "ARS",
                "fuente": "ARCA",
                "origen": "PDF_MONEDA_EXTRANJERA",
            })
        
        # Buscar dólar en divisas
        divisas = raw.get('divisas', [])
        dolar_divisa = self._find_dolar(divisas)
        
        if dolar_divisa:
            result.append({
                "concepto": "BP_DOLAR_DIVISA_COMP_31_12",
                "impuesto": "BIENES_PERSONALES",
                "anio": self.year,
                "valor": self._to_number(dolar_divisa.get('comprador')),
                "desde": None,
                "hasta": None,
                "monto_fijo": None,
                "porcentaje": None,
                "excedente_desde": None,
                "unidad": "ARS",
                "fuente": "ARCA",
                "origen": "PDF_MONEDA_EXTRANJERA",
            })
            
            result.append({
                "concepto": "BP_DOLAR_DIVISA_VEND_31_12",
                "impuesto": "BIENES_PERSONALES",
                "anio": self.year,
                "valor": self._to_number(dolar_divisa.get('vendedor')),
                "desde": None,
                "hasta": None,
                "monto_fijo": None,
                "porcentaje": None,
                "excedente_desde": None,
                "unidad": "ARS",
                "fuente": "ARCA",
                "origen": "PDF_MONEDA_EXTRANJERA",
            })
        
        self.logger.debug(f"Cotizaciones normalizadas: {len(result)}")
        return result
    
    # === HELPERS ===
    
    def _to_number(self, x) -> float:
        """Convierte a número."""
        if x is None:
            return None
        if isinstance(x, (int, float)):
            return float(x)
        
        s = str(x).strip()
        
        if s.endswith("%"):
            s = s.replace("%", "").strip()
        
        s = s.replace("$", "").replace(" ", "")
        s = s.replace(".", "")
        s = s.replace(",", ".")
        
        if "adelante" in s.lower():
            return None
        
        try:
            return float(s)
        except:
            return None
    
    def _extract_tramos_from_table(self, rows: list) -> list:
        """Extrae tramos de una tabla HTML."""
        tramos = []
        
        for r in rows:
            if not isinstance(r, list) or len(r) < 4:
                continue
            
            if len(r) >= 5:
                desde, hasta, pagaran, porc, exced = r[0], r[1], r[2], r[3], r[4]
            else:
                continue
            
            # Descartar headers
            if "más de" in str(desde).lower() or "valor total" in str(desde).lower():
                continue
            
            # Debe tener porcentaje
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
    
    def _find_dolar(self, lista: list) -> dict:
        """Busca entrada de dólar en lista."""
        for item in lista:
            desc = (item.get("descripcion") or "").upper()
            if "DOLAR" in desc or "DÓLAR" in desc or "DOLLAR" in desc:
                return item
        return None
