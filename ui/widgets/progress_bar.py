"""
Kairos Tutor - Кастомный прогресс-бар
Стилизованный виджет для отображения прогресса
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class CustomProgressBar(QWidget):
    """
    Кастомный виджет прогресс-бара с текстовой меткой.
    
    Использует стили из theme.qss через objectName.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Приватные переменные
        self._value = 0
        self._maximum = 100
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса виджета"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Прогресс-бар (стандартный PyQt6 с кастомными стилями)
        from PyQt6.QtWidgets import QProgressBar
        self._progress_bar = QProgressBar()
        self._progress_bar.setObjectName("ProgressBar")
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFormat("%p%")
        
        # Метка с текстовым описанием
        self._label = QLabel("Прогресс: 0%")
        self._label.setObjectName("secondaryLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self._progress_bar)
        layout.addWidget(self._label)
    
    def set_value(self, value: int):
        """
        Установка значения прогресса.
        
        Args:
            value: Значение от 0 до 100
        """
        self._value = max(0, min(100, value))
        self._progress_bar.setValue(self._value)
        self._label.setText(f"Прогресс: {self._value}%")
    
    def set_progress(self, completed: int, total: int):
        """
        Установка прогресса на основе выполненных и общих задач.
        
        Args:
            completed: Количество выполненных задач
            total: Общее количество задач
        """
        if total == 0:
            self.set_value(0)
        else:
            percentage = int((completed / total) * 100)
            self.set_value(percentage)
            self._label.setText(f"Прогресс: {completed}/{total} ({percentage}%)")
    
    def get_value(self) -> int:
        """Получение текущего значения прогресса"""
        return self._value
    
    def reset(self):
        """Сброс прогресса к 0"""
        self.set_value(0)