"""
Orquestador principal - Coordina descarga, parseo, normalización y cache.
"""
from pathlib import Path
from typing import Optional, Dict, List
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import RAW_DIR, NORMALIZED_DIR, FILES_DIR
from config.constants import YEARS_WITH_SUBPERIODS
from core.cache_manager import CacheManager
from utils.logger import get_logger
from parsers.art30_parser import Art30SingleParser


# Imports de parsers (los crearemos después)
from parsers.art30_parser import Art30Parser
from parsers.art94_parser import Art94Parser
from parsers.bp_alicuotas_parser import BPAlicuotasParser
from parsers.bp_minimo_parser import BPMinimoParser
from parsers.monedas_parser import MonedasParser

# Imports de normalizers
from normalizers.arca_normalizer import ARCANormalizer

logger = get_logger(__name__)


class ARCAOrchestrator:
    """
    Orquestador principal del sistema.
    
    Coordina:
    1. Verificación de cache
    2. Descarga de fuentes
    3. Parseo de datos
    4. Normalización a formato Excel
    5. Guardado en cache
    """
    
    def __init__(self, year: int, force_refresh: bool = False):
        self.year = year
        self.force_refresh = force_refresh
        self.cache_manager = CacheManager(year)
        
        # Directorios de trabajo
        self.raw_dir = RAW_DIR / str(year)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Inicializando orquestador para año {year}")
        if force_refresh:
            logger.warning("Modo FORCE REFRESH activado - ignorando cache")
    
    def run(self) -> List[Dict]:
        """
        Ejecuta el pipeline completo.
        
        Returns:
            Lista de parámetros normalizados
        """
        logger.info("="*70)
        logger.info(f"ACTUALIZACIÓN PARÁMETROS ARCA - AÑO {self.year}")
        logger.info("="*70)
        
        # 1. Verificar cache
        if not self.force_refresh:
            cached_data = self.cache_manager.get()
            if cached_data:
                logger.info(f"✓ Usando cache existente ({len(cached_data)} registros)")
                return cached_data
        
        logger.info("→ Generando nuevos datos...")
        
        # 2. Parsear todas las fuentes
        raw_data = self._parse_all_sources()
        
        # 3. Normalizar a formato Excel
        normalized_data = self._normalize_data(raw_data)
        
        # 4. Validar
        self._validate_data(normalized_data)
        
        # 5. Guardar en cache
        sources_info = self._build_sources_info(raw_data)
        self.cache_manager.save(normalized_data, sources_info)
        
        logger.info("="*70)
        logger.info(f"✓ ACTUALIZACIÓN COMPLETADA - {len(normalized_data)} registros")
        logger.info("="*70)
        
        return normalized_data
    
    def _parse_all_sources(self) -> Dict:
        """
        Parsea todas las fuentes de datos.
        
        Returns:
            Diccionario con datos crudos por fuente
        """
        logger.info("\n📥 PARSEANDO FUENTES...")
        
        raw_data = {}
        
        # Ganancias - Deducciones (Art. 30)
        logger.info("\n1️⃣  Deducciones Personales (Art. 30)")
        try:
            parser = Art30SingleParser(self.year)

            raw_data["deducciones"] = parser.parse(pdf_dir=FILES_DIR)   # FILES_DIR = carpeta donde están los pdf

            logger.info(f"   ✓ {len(raw_data['deducciones'].get('items', {}))} deducciones extraídas")
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            raw_data['deducciones'] = None
        
        # Ganancias - Escalas (Art. 94)
        logger.info("\n2️⃣  Escalas Ganancias (Art. 94)")
        try:
            # Si el año tiene subperíodos, parsear todos y unir
            if self.year in YEARS_WITH_SUBPERIODS:
                raw_data['escalas'] = self._parse_escalas_con_subperiodos()
            else:
                parser = Art94Parser(self.year, FILES_DIR)
                raw_data['escalas'] = parser.parse()
            
            tramos = raw_data['escalas'] if isinstance(raw_data['escalas'], list) else []
            logger.info(f"   ✓ {len(tramos)} tramos extraídos")
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            raw_data['escalas'] = None
        
        # Bienes Personales - Alícuotas (HTML)
        logger.info("\n3️⃣  Alícuotas Bienes Personales")
        try:
            parser = BPAlicuotasParser()
            raw_data['bp_alicuotas'] = parser.parse()
            logger.info(f"   ✓ Alícuotas extraídas")
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            raw_data['bp_alicuotas'] = None
        
        # Bienes Personales - Mínimo (HTML)
        logger.info("\n4️⃣  Mínimo No Imponible BP")
        try:
            parser = BPMinimoParser()
            raw_data['bp_minimo'] = parser.parse()
            logger.info(f"   ✓ Mínimo extraído")
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            raw_data['bp_minimo'] = None
        
        # Bienes Personales - Cotización dólar (PDF)
        logger.info("\n5️⃣  Cotización Moneda Extranjera")
        try:
            parser = MonedasParser(self.year, FILES_DIR)
            raw_data['monedas'] = parser.parse()
            logger.info(f"   ✓ Cotizaciones extraídas")
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            raw_data['monedas'] = None
        
        return raw_data
    
    def _parse_escalas_con_subperiodos(self) -> list:
        """
        Parsea escalas de un año con subperíodos y las unifica.
        
        Por ejemplo, 2023 tiene "hasta septiembre" y "desde octubre".
        Debemos usar la versión "desde octubre" para el cálculo anual.
        """
        logger.info("   → Año con subperíodos detectado")
        
        subperiodos = YEARS_WITH_SUBPERIODS[self.year]
        
        # Intentar parsear cada subperíodo
        escalas_por_periodo = {}
        for periodo in subperiodos:
            try:
                # TODO: Implementar lógica de descarga por subperíodo
                # Por ahora, asumimos que el PDF tiene un nombre específico
                parser = Art94Parser(self.year, FILES_DIR, subperiodo=periodo['name'])
                escalas_por_periodo[periodo['name']] = parser.parse()
                logger.info(f"      ✓ Subperíodo '{periodo['name']}' parseado")
            except:
                logger.warning(f"      ⚠️  Subperíodo '{periodo['name']}' no disponible")
        
        # Usar el último subperíodo (el más reciente)
        if escalas_por_periodo:
            ultimo_periodo = subperiodos[-1]['name']
            logger.info(f"   → Usando subperíodo '{ultimo_periodo}' (más reciente)")
            return escalas_por_periodo.get(ultimo_periodo, [])
        
        return []
    
    def _normalize_data(self, raw_data: Dict) -> List[Dict]:
        """
        Normaliza datos crudos a formato Excel.
        
        Args:
            raw_data: Diccionario con datos crudos de parsers
        
        Returns:
            Lista de diccionarios en formato Excel
        """
        logger.info("\n🔄 NORMALIZANDO DATOS...")
        
        normalizer = ARCANormalizer(self.year)
        
        parametros = []
        
        # Normalizar cada fuente
        if raw_data.get('deducciones'):
            parametros.extend(normalizer.normalize_deducciones(raw_data['deducciones']))
        
        if raw_data.get('escalas'):
            parametros.extend(normalizer.normalize_escalas(raw_data['escalas']))
        
        if raw_data.get('bp_alicuotas'):
            parametros.extend(normalizer.normalize_bp_alicuotas(raw_data['bp_alicuotas']))
        
        if raw_data.get('bp_minimo'):
            parametros.extend(normalizer.normalize_bp_minimo(raw_data['bp_minimo']))
        
        if raw_data.get('monedas'):
            parametros.extend(normalizer.normalize_monedas(raw_data['monedas']))
        
        logger.info(f"   ✓ {len(parametros)} registros normalizados")
        
        return parametros
    
    def _validate_data(self, data: List[Dict]):
        """
        Valida datos normalizados.
        
        Args:
            data: Lista de parámetros normalizados
        """
        logger.info("\n✅ VALIDANDO DATOS...")
        
        # Contar registros por tipo
        counts = {}
        for item in data:
            concepto_prefix = item['concepto'].split('_')[0] + '_' + item['concepto'].split('_')[1]
            counts[concepto_prefix] = counts.get(concepto_prefix, 0) + 1
        
        # Mostrar resumen
        logger.info("\n   Registros por tipo:")
        for prefix, count in sorted(counts.items()):
            logger.info(f"      {prefix}: {count}")
        
        # Validaciones básicas
        warnings = []
        
        # Verificar que haya al menos algunos registros de cada tipo
        if counts.get('GAN_DED', 0) < 5:
            warnings.append("Pocas deducciones de Ganancias")
        
        if counts.get('GAN_ESCALA', 0) < 8:
            warnings.append("Pocas escalas de Ganancias")
        
        if counts.get('BP_ALICUOTA', 0) < 4:
            warnings.append("Pocas alícuotas de BP")
        
        if warnings:
            logger.warning("\n   ⚠️  Advertencias:")
            for warning in warnings:
                logger.warning(f"      - {warning}")
        else:
            logger.info("   ✓ Validación OK")
    
    def _build_sources_info(self, raw_data: Dict) -> Dict:
        """Construye información de fuentes para metadata."""
        return {
            "deducciones": bool(raw_data.get('deducciones')),
            "escalas": bool(raw_data.get('escalas')),
            "bp_alicuotas": bool(raw_data.get('bp_alicuotas')),
            "bp_minimo": bool(raw_data.get('bp_minimo')),
            "monedas": bool(raw_data.get('monedas')),
        }
