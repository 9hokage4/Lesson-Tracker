"""
Kairos Tutor - Конфигурация приложения
Загрузка переменных окружения из .env файла
"""

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class Config:
    """
    Конфигурация приложения.
    
    Все приватные данные хранятся в переменных с префиксом _.
    Публичный доступ только через @property.
    """
    
    _instance: Optional['Config'] = None
    
    def __new__(cls):
        """Singleton паттерн для конфигурации"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Загрузка переменных окружения
        if load_dotenv:
            env_path = Path(__file__).parent.parent / '.env'
            load_dotenv(env_path)
        
        # Приватные переменные
        self._db_path = os.getenv('DB_PATH', 'database/kairos.db')
        self._app_name = os.getenv('APP_NAME', 'Kairos Tutor')
        self._debug = os.getenv('DEBUG', 'False') == 'True'
        self._styles_path = os.getenv('STYLES_PATH', 'styles/theme.qss')
        self._log_level = os.getenv('LOG_LEVEL', 'INFO')
        self._log_path = os.getenv('LOG_PATH', 'logs/app.log')
        self._export_path = os.getenv('EXPORT_PATH', 'exports/')
        
        # Инициализация путей
        self._init_paths()
        
        self._initialized = True
    
    def _init_paths(self):
        """Создание необходимых папок если они не существуют"""
        base_path = Path(__file__).parent.parent
        
        # Путь к базе данных
        db_full_path = base_path / self._db_path
        db_full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Путь к логам
        log_full_path = base_path / self._log_path
        log_full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Путь к экспорту
        export_full_path = base_path / self._export_path
        export_full_path.mkdir(parents=True, exist_ok=True)
    
    # ============================================
    # Публичные свойства (только чтение)
    # ============================================
    
    @property
    def db_path(self) -> str:
        return self._db_path
    
    @property
    def db_full_path(self) -> Path:
        return Path(__file__).parent.parent / self._db_path
    
    @property
    def app_name(self) -> str:
        return self._app_name
    
    @property
    def debug(self) -> bool:
        return self._debug
    
    @property
    def styles_path(self) -> str:
        return self._styles_path
    
    @property
    def styles_full_path(self) -> Path:
        return Path(__file__).parent.parent / self._styles_path
    
    @property
    def log_level(self) -> str:
        return self._log_level
    
    @property
    def log_path(self) -> str:
        return self._log_path
    
    @property
    def export_path(self) -> str:
        return self._export_path
    
    @property
    def export_full_path(self) -> Path:
        return Path(__file__).parent.parent / self._export_path
    
    def is_production(self) -> bool:
        return not self._debug
    
    def is_development(self) -> bool:
        return self._debug


# Глобальный экземпляр конфигурации
config = Config()