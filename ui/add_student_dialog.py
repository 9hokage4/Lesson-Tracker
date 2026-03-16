"""
Kairos Tutor - Диалог добавления нового ученика
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from utils.helpers import generate_student_uuid


class AddStudentDialog(QDialog):
    """Диалоговое окно для добавления нового ученика"""
    
    # Сигнал об успешном добавлении ученика
    student_added = pyqtSignal()
    
    def __init__(self, database, parent=None):
        super().__init__(parent)
        
        # Приватные переменные
        self._db = database
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Настройка интерфейса диалога"""
        self.setWindowTitle("Добавить ученика")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        # Главный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Заголовок
        title_label = QLabel("Новый ученик")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # Поле ввода имени
        name_label = QLabel("Имя и фамилия:")
        name_label.setObjectName("textLabel")
        layout.addWidget(name_label)
        
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Иванов Иван")
        self._name_input.setFixedHeight(45)
        layout.addWidget(self._name_input)
        
        # Поле для отображения UUID (только чтение)
        uuid_label = QLabel("Уникальный ID:")
        uuid_label.setObjectName("textLabel")
        layout.addWidget(uuid_label)
        
        self._uuid_input = QLineEdit()
        self._uuid_input.setReadOnly(True)
        self._uuid_input.setFixedHeight(45)
        self._uuid_input.setText(generate_student_uuid())
        layout.addWidget(self._uuid_input)
        
        # Кнопки действий
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Кнопка отмены
        self._cancel_button = QPushButton("Отмена")
        self._cancel_button.setObjectName("dangerButton")
        self._cancel_button.setFixedHeight(45)
        self._cancel_button.clicked.connect(self.reject)
        
        # Кнопка добавления
        self._add_button = QPushButton("Добавить")
        self._add_button.setObjectName("successButton")
        self._add_button.setFixedHeight(45)
        self._add_button.clicked.connect(self._add_student)
        
        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._add_button)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Настройка соединений сигналов и слотов"""
        self._name_input.textChanged.connect(self._validate_input)
    
    def _validate_input(self):
        """Валидация ввода пользователя"""
        name = self._name_input.text().strip()
        
        # Блокировка кнопки если имя пустое
        self._add_button.setEnabled(len(name) > 0)
    
    def _add_student(self):
        """Добавление ученика в базу данных"""
        name = self._name_input.text().strip()
        uuid = self._uuid_input.text().strip()
        
        # Валидация
        if not name:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите имя ученика"
            )
            return
        
        try:
            # Добавление в БД
            self._db.add_student(name=name, student_uuid=uuid)
            
            # Уведомление об успехе
            QMessageBox.information(
                self,
                "Успешно",
                f"Ученик {name} добавлен!\nID: {uuid}"
            )
            
            # Отправка сигнала об успешном добавлении
            self.student_added.emit()
            
            # Закрытие диалога
            self.accept()
            
        except Exception as e:
            # Обработка ошибок
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить ученика:\n{str(e)}"
            )
    
    def get_student_data(self):
        """
        Получение данных ученика.
        
        Returns:
            dict: Данные ученика (name, uuid)
        """
        return {
            'name': self._name_input.text().strip(),
            'uuid': self._uuid_input.text().strip()
        }