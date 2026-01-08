"""
Sistema de logging centralizado.
"""
import logging
from datetime import datetime
from pathlib import Path

from config.settings import (
    LOGS_DIR,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_FILENAME_TEMPLATE,
)


class ARCALogger:
    """Logger configurado para el sistema ARCA."""
    
    _loggers = {}
    _file_handler = None
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Obtiene un logger configurado.
        
        Args:
            name: Nombre del logger (típicamente __name__ del módulo)
        
        Returns:
            Logger configurado
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Evitar duplicados
        if logger.handlers:
            cls._loggers[name] = logger
            return logger
        
        # Handler de consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Handler de archivo (compartido por todos los loggers)
        if cls._file_handler is None:
            cls._file_handler = cls._create_file_handler()
        
        logger.addHandler(cls._file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def _create_file_handler(cls) -> logging.FileHandler:
        """Crea handler de archivo con timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = LOG_FILENAME_TEMPLATE.format(timestamp=timestamp)
        log_path = LOGS_DIR / log_filename
        
        handler = logging.FileHandler(log_path, encoding='utf-8')
        handler.setLevel(getattr(logging, LOG_LEVEL))
        
        formatter = logging.Formatter(
            LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT
        )
        handler.setFormatter(formatter)
        
        print(f"📝 Log: {log_path.name}")
        
        return handler
    
    @classmethod
    def get_current_log_file(cls) -> Path:
        """Obtiene el path del archivo de log actual."""
        if cls._file_handler:
            return Path(cls._file_handler.baseFilename)
        return None


# Función helper para obtener logger fácilmente
def get_logger(name: str) -> logging.Logger:
    """Helper function para obtener logger."""
    return ARCALogger.get_logger(name)
