"""
Kairos Tutor - Точка входа в приложение
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication, Qt

from core.database import Database
from core.config import config


def load_stylesheet(app: QApplication) -> None:
    """
    Загрузка QSS стилей из файла.
    
    Args:
        app: Экземпляр QApplication
    """
    style_path = config.styles_full_path
    
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Stylesheet not found at {style_path}")


def initialize_database() -> Database:
    """
    Инициализация базы данных.
    
    Returns:
        Database: Экземпляр базы данных
    """
    db = Database()
    db.create_tables()
    return db


def main():
    """Основная функция запуска приложения"""
    
    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)
    
    # Загрузка стилей
    load_stylesheet(app)
    
    # Инициализация базы данных
    _db = initialize_database()
    
    # Создание и показ главного окна
    from ui.main_window import MainWindow
    window = MainWindow(_db)
    window.show()
    
    # Запуск цикла событий
    sys.exit(app.exec())


if __name__ == "__main__":
    main()