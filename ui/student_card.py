"""
Kairos Tutor - Виджет карточки ученика
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt


class StudentCard(QWidget):
    """Карточка ученика для отображения в сетке"""
    
    clicked = pyqtSignal(int)  # Сигнал с ID ученика при клике
    
    def __init__(self, student_data):
        super().__init__()
        
        # Приватные переменные
        self._student_id = student_data['id']
        self._student_uuid = student_data['student_uuid']
        self._student_name = student_data['name']
        self._status = student_data['status']
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса карточки"""
        self.setObjectName("StudentCard")
        self.setFixedSize(350, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Главный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Верхняя часть: ID и имя
        top_layout = QHBoxLayout()
        
        # ID ученика
        self._id_label = QLabel(f"#{self._student_uuid}")
        self._id_label.setObjectName("studentId")
        
        # Имя ученика
        self._name_label = QLabel(self._student_name)
        self._name_label.setObjectName("titleLabel")
        self._name_label.setWordWrap(True)
        
        top_layout.addWidget(self._id_label)
        top_layout.addStretch()
        top_layout.addWidget(self._name_label)
        
        # Статус
        self._status_label = QLabel(self._get_status_text())
        self._status_label.setObjectName(self._get_status_class())
        
        # Кнопка открытия
        self._open_button = QPushButton("Открыть профиль →")
        self._open_button.setObjectName("primaryButton")
        self._open_button.setFixedHeight(40)
        
        # Добавление в layout
        layout.addLayout(top_layout)
        layout.addWidget(self._status_label)
        layout.addStretch()
        layout.addWidget(self._open_button)
    
    def _get_status_text(self) -> str:
        """Получение текста статуса"""
        status_map = {
            'active': 'Активен',
            'paused': 'На паузе',
            'archived': 'Архивирован'
        }
        return status_map.get(self._status, 'Активен')
    
    def _get_status_class(self) -> str:
        """Получение CSS класса для статуса"""
        status_map = {
            'active': 'statusCompleted',
            'paused': 'statusRescheduled',
            'archived': 'statusCancelled'
        }
        return status_map.get(self._status, 'statusCompleted')
    
    def mousePressEvent(self, event):
        """Обработка клика по карточке"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._student_id)