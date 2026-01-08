"""
Cache Manager - Gestión inteligente de cache con metadata.

El cache es "eterno" por defecto - se crea una vez y se reutiliza.
Solo se actualiza con --force o si no existe.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib

from config.settings import (
    CACHE_DIR,
    CACHE_METADATA_FILENAME,
    CACHE_ENABLED,
)


class CacheManager:
    """Gestiona el cache de parámetros ARCA por año."""
    
    def __init__(self, year: int):
        self.year = year
        self.cache_dir = CACHE_DIR / str(year)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivos
        self.json_file = self.cache_dir / f"parametros_arca_{year}.json"
        self.metadata_file = self.cache_dir / CACHE_METADATA_FILENAME
    
    def exists(self) -> bool:
        """Verifica si existe cache válido para este año."""
        if not CACHE_ENABLED:
            return False
        
        return self.json_file.exists() and self.metadata_file.exists()
    
    def get(self) -> Optional[list]:
        """
        Obtiene datos del cache si existe.
        
        Returns:
            Lista de parámetros o None si no hay cache.
        """
        if not self.exists():
            return None
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Log de uso de cache
            print(f"✓ Cache encontrado: {self.json_file.name}")
            self._log_cache_usage()
            
            return data
        
        except Exception as e:
            print(f"⚠️  Error leyendo cache: {e}")
            return None
    
    def save(self, data: list, sources: Dict[str, Any] = None):
        """
        Guarda datos en cache con metadata.
        
        Args:
            data: Lista de parámetros normalizados
            sources: Diccionario con info de fuentes usadas
        """
        if not CACHE_ENABLED:
            return
        
        # Guardar JSON
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Guardar metadata
        metadata = self._create_metadata(data, sources)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Cache guardado: {self.json_file.name}")
        print(f"  Registros: {len(data)}")
    
    def invalidate(self):
        """Elimina el cache de este año."""
        if self.json_file.exists():
            self.json_file.unlink()
        if self.metadata_file.exists():
            self.metadata_file.unlink()
        
        print(f"✓ Cache eliminado para año {self.year}")
    
    def get_metadata(self) -> Optional[Dict]:
        """Obtiene metadata del cache."""
        if not self.metadata_file.exists():
            return None
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def _create_metadata(self, data: list, sources: Dict = None) -> Dict:
        """Crea metadata para el cache."""
        return {
            "year": self.year,
            "created_at": datetime.now().isoformat(),
            "record_count": len(data),
            "data_hash": self._compute_hash(data),
            "sources": sources or {},
            "version": "1.0",
        }
    
    def _compute_hash(self, data: list) -> str:
        """Calcula hash SHA256 de los datos."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    def _log_cache_usage(self):
        """Registra uso del cache en metadata."""
        metadata = self.get_metadata()
        if not metadata:
            return
        
        if "usage_count" not in metadata:
            metadata["usage_count"] = 0
        
        metadata["usage_count"] += 1
        metadata["last_used"] = datetime.now().isoformat()
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def list_cached_years() -> list:
        """Lista todos los años con cache disponible."""
        if not CACHE_DIR.exists():
            return []
        
        years = []
        for year_dir in CACHE_DIR.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                cache_file = year_dir / f"parametros_arca_{year_dir.name}.json"
                if cache_file.exists():
                    years.append(int(year_dir.name))
        
        return sorted(years)
    
    @staticmethod
    def get_cache_info() -> Dict:
        """Obtiene información de todos los caches."""
        info = {
            "cached_years": [],
            "total_size_mb": 0,
        }
        
        for year in CacheManager.list_cached_years():
            cm = CacheManager(year)
            metadata = cm.get_metadata()
            
            size_bytes = cm.json_file.stat().st_size if cm.json_file.exists() else 0
            
            info["cached_years"].append({
                "year": year,
                "created_at": metadata.get("created_at") if metadata else None,
                "record_count": metadata.get("record_count") if metadata else 0,
                "size_kb": size_bytes / 1024,
            })
            
            info["total_size_mb"] += size_bytes / (1024 * 1024)
        
        return info
