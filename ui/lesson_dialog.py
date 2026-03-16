"""
Kairos Tutor - Диалог планирования/завершения урока
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QDateEdit, QTextEdit,
    QMessageBox, QGroupBox
)
from PyQt6.QtCore import pyqtSignal, QDate

from utils.helpers import get_recurrence_options, get_lesson_status_options


class LessonDialog(QDialog):
    """Диалоговое окно для планирования или завершения урока"""
    
    # Сигнал о сохранении урока
    lesson_saved = pyqtSignal()
    
    def __init__(self, database, student_id, parent=None):
        super().__init__(parent)
        
        # Приватные переменные
        self._db = database
        self._student_id = student_id
        self._lesson_id = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса диалога"""
        self.setWindowTitle("Планирование урока")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # Главный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Заголовок
        title_label = QLabel("📅 Новый урок")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # Дата урока
        date_group = QGroupBox("Дата и время")
        date_layout = QVBoxLayout(date_group)
        
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setFixedHeight(45)
        date_layout.addWidget(self._date_edit)
        
        layout.addWidget(date_group)
        
        # Повторение
        recurrence_group = QGroupBox("Повторение")
        recurrence_layout = QVBoxLayout(recurrence_group)
        
        self._recurrence_combo = QComboBox()
        for display, value in get_recurrence_options():
            self._recurrence_combo.addItem(display, value)
        self._recurrence_combo.setFixedHeight(45)
        recurrence_layout.addWidget(self._recurrence_combo)
        
        layout.addWidget(recurrence_group)
        
        # Заметки
        notes_group = QGroupBox("Заметки к уроку")
        notes_layout = QVBoxLayout(notes_group)
        
        self._notes_edit = QTextEdit()
        self._notes_edit.setPlaceholderText("Тема урока, домашнее задание...")
        self._notes_edit.setFixedHeight(100)
        notes_layout.addWidget(self._notes_edit)
        
        layout.addWidget(notes_group)
        
        # Оценка
        grade_group = QGroupBox("Оценка (после урока)")
        grade_layout = QVBoxLayout(grade_group)
        
        self._grade_combo = QComboBox()
        self._grade_combo.addItem("Не выставлена", "")
        self._grade_combo.addItem("5 - Отлично", "5")
        self._grade_combo.addItem("4 - Хорошо", "4")
        self._grade_combo.addItem("3 - Удовл.", "3")
        self._grade_combo.addItem("2 - Неуд.", "2")
        self._grade_combo.setFixedHeight(45)
        grade_layout.addWidget(self._grade_combo)
        
        layout.addWidget(grade_group)
        
        # Кнопки действий
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self._cancel_button = QPushButton("Отмена")
        self._cancel_button.setObjectName("dangerButton")
        self._cancel_button.setFixedHeight(45)
        self._cancel_button.clicked.connect(self.reject)
        
        self._save_button = QPushButton("Сохранить")
        self._save_button.setObjectName("successButton")
        self._save_button.setFixedHeight(45)
        self._save_button.clicked.connect(self._save_lesson)
        
        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._save_button)
        
        layout.addLayout(button_layout)
    
    def _save_lesson(self):
        """Сохранение урока в базу данных"""
        date = self._date_edit.date().toString("yyyy-MM-dd")
        recurrence = self._recurrence_combo.currentData()
        notes = self._notes_edit.toPlainText()
        grade = self._grade_combo.currentData()
        
        try:
            # Добавление урока
            self._db.add_lesson(
                student_id=self._student_id,
                scheduled_date=date,
                recurrence_type=recurrence
            )
            
            # Если есть оценка - добавляем результат
            if grade:
                self._db.add_result(
                    student_id=self._student_id,
                    grade=grade,
                    date=date
                )
            
            # Отправка сигнала
            self.lesson_saved.emit()
            
            # Закрытие диалога
            self.accept()
            
            QMessageBox.information(
                self,
                "Успешно",
                "Урок успешно запланирован!"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить урок:\n{str(e)}"
            )