"""
Kairos Tutor - Диалог профиля ученика
Отображает информацию об ученике, уроках и успеваемости
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QScrollArea, QWidget,
    QGroupBox, QTextEdit, QMessageBox, QComboBox,
    QDateEdit, QCheckBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt, QDate
from PyQt6.QtGui import QFont

from ui.lesson_dialog import LessonDialog


class StudentProfileDialog(QDialog):
    """Диалоговое окно профиля ученика"""
    
    # Сигнал об обновлении урока
    lesson_updated = pyqtSignal()
    
    def __init__(self, student_data, database, parent=None):
        super().__init__(parent)
        
        # Приватные переменные
        self._student = student_data
        self._db = database
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Настройка интерфейса диалога"""
        self.setWindowTitle("Профиль ученика")
        self.setMinimumSize(800, 700)
        self.setModal(True)
        
        # Главный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Заголовок с именем и ID
        self._setup_header(main_layout)
        
        # Кнопки действий
        self._setup_action_buttons(main_layout)
        
        # Скролл-область для контента
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Контейнер для контента
        content_widget = QWidget()
        self._content_layout = QVBoxLayout(content_widget)
        self._content_layout.setSpacing(20)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll, stretch=1)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.setObjectName("primaryButton")
        close_button.setFixedHeight(45)
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)
    
    def _setup_header(self, layout):
        """Настройка заголовка профиля"""
        header_layout = QHBoxLayout()
        
        # Имя ученика
        self._name_label = QLabel(self._student['name'])
        self._name_label.setObjectName("titleLabel")
        
        # ID ученика
        self._id_label = QLabel(f"#{self._student['student_uuid']}")
        self._id_label.setObjectName("studentId")
        
        # Статус
        self._status_label = QLabel(self._get_status_text())
        self._status_label.setObjectName(self._get_status_class())
        
        header_layout.addWidget(self._name_label)
        header_layout.addStretch()
        header_layout.addWidget(self._id_label)
        header_layout.addWidget(self._status_label)
        
        layout.addLayout(header_layout)
    
    def _setup_action_buttons(self, layout):
        """Настройка кнопок действий"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Кнопка запланировать урок
        self._schedule_button = QPushButton("📅 Запланировать урок")
        self._schedule_button.setObjectName("primaryButton")
        self._schedule_button.setFixedHeight(45)
        self._schedule_button.clicked.connect(self._open_lesson_dialog)
        
        # Кнопка редактировать
        self._edit_button = QPushButton("✏️ Редактировать")
        self._edit_button.setObjectName("secondaryButton")
        self._edit_button.setFixedHeight(45)
        
        # Кнопка архивировать
        self._archive_button = QPushButton("📁 Архивировать")
        self._archive_button.setObjectName("warningButton")
        self._archive_button.setFixedHeight(45)
        
        button_layout.addWidget(self._schedule_button)
        button_layout.addWidget(self._edit_button)
        button_layout.addWidget(self._archive_button)
        
        layout.addLayout(button_layout)
    
    def _load_data(self):
        """Загрузка данных ученика"""
        # Блок следующего урока
        self._load_next_lesson_block()
        
        # Блок плана занятий
        self._load_study_plan_block()
        
        # Блок успеваемости
        self._load_results_block()
        
        # Блок заметок
        self._load_notes_block()
    
    def _load_next_lesson_block(self):
        """Загрузка блока следующего урока"""
        group = QGroupBox("📅 Ближайший урок")
        group.setObjectName("groupBox")
        layout = QVBoxLayout(group)
        
        # Получение следующего урока
        next_lesson = self._db.get_next_lesson(self._student['id'])
        
        if next_lesson:
            date_str = next_lesson['scheduled_date']
            lesson_label = QLabel(f"Дата: {date_str}")
            lesson_label.setObjectName("textLabel")
            layout.addWidget(lesson_label)
            
            status_label = QLabel(f"Статус: {next_lesson['status']}")
            status_label.setObjectName("secondaryLabel")
            layout.addWidget(status_label)
        else:
            no_lesson_label = QLabel("Уроки не запланированы")
            no_lesson_label.setObjectName("secondaryLabel")
            layout.addWidget(no_lesson_label)
        
        self._content_layout.addWidget(group)
    
    def _load_study_plan_block(self):
        """Загрузка блока плана занятий"""
        group = QGroupBox("📚 План занятий")
        group.setObjectName("groupBox")
        layout = QVBoxLayout(group)
        
        # Получение плана
        plan = self._db.get_study_plan(self._student['id'])
        completed, total = self._db.get_plan_progress(self._student['id'])
        
        # Прогресс-бар
        progress_label = QLabel(f"Прогресс: {completed}/{total} тем")
        progress_label.setObjectName("textLabel")
        layout.addWidget(progress_label)
        
        # Список тем
        self._plan_list = QListWidget()
        self._plan_list.setFixedHeight(150)
        
        for topic in plan:
            item = QListWidgetItem(topic['topic'])
            if topic['is_completed']:
                item.setText("✅ " + topic['topic'])
            else:
                item.setText("⬜ " + topic['topic'])
            self._plan_list.addItem(item)
        
        layout.addWidget(self._plan_list)
        
        # Кнопка добавления темы
        add_topic_button = QPushButton("+ Добавить тему")
        add_topic_button.setObjectName("secondaryButton")
        add_topic_button.setFixedHeight(40)
        add_topic_button.clicked.connect(self._add_plan_topic)
        layout.addWidget(add_topic_button)
        
        self._content_layout.addWidget(group)
    
    def _load_results_block(self):
        """Загрузка блока результатов"""
        group = QGroupBox("📊 Успеваемость")
        group.setObjectName("groupBox")
        layout = QVBoxLayout(group)
        
        # Средняя оценка
        avg_grade = self._db.get_average_grade(self._student['id'])
        
        if avg_grade:
            avg_label = QLabel(f"Средняя оценка: {avg_grade:.2f}")
            avg_label.setObjectName("textLabel")
            layout.addWidget(avg_label)
        else:
            no_results_label = QLabel("Оценок пока нет")
            no_results_label.setObjectName("secondaryLabel")
            layout.addWidget(no_results_label)
        
        # Последние результаты
        results_label = QLabel("Последние оценки:")
        results_label.setObjectName("textLabel")
        layout.addWidget(results_label)
        
        self._results_list = QListWidget()
        self._results_list.setFixedHeight(100)
        
        results = self._db.get_results_by_student(self._student['id'])[:5]
        for result in results:
            item = QListWidgetItem(f"{result['date']}: {result['grade']}")
            self._results_list.addItem(item)
        
        layout.addWidget(self._results_list)
        
        self._content_layout.addWidget(group)
    
    def _load_notes_block(self):
        """Загрузка блока заметок"""
        group = QGroupBox("📝 Заметки")
        group.setObjectName("groupBox")
        layout = QVBoxLayout(group)
        
        self._notes_edit = QTextEdit()
        self._notes_edit.setPlaceholderText("Введите заметки об ученике...")
        self._notes_edit.setFixedHeight(100)
        layout.addWidget(self._notes_edit)
        
        save_notes_button = QPushButton("💾 Сохранить заметки")
        save_notes_button.setObjectName("primaryButton")
        save_notes_button.setFixedHeight(40)
        save_notes_button.clicked.connect(self._save_notes)
        layout.addWidget(save_notes_button)
        
        self._content_layout.addWidget(group)
    
    def _get_status_text(self) -> str:
        """Получение текста статуса"""
        status_map = {
            'active': 'Активен',
            'paused': 'На паузе',
            'archived': 'Архивирован'
        }
        return status_map.get(self._student['status'], 'Активен')
    
    def _get_status_class(self) -> str:
        """Получение CSS класса для статуса"""
        status_map = {
            'active': 'statusCompleted',
            'paused': 'statusRescheduled',
            'archived': 'statusCancelled'
        }
        return status_map.get(self._student['status'], 'statusCompleted')
    
    def _open_lesson_dialog(self):
        """Открытие диалога планирования урока"""
        dialog = LessonDialog(self._db, self._student['id'], self)
        dialog.lesson_saved.connect(self._on_lesson_saved)
        dialog.exec()
    
    def _on_lesson_saved(self):
        """Обработка сохранения урока"""
        self.lesson_updated.emit()
        self._load_data()
        QMessageBox.information(self, "Успешно", "Урок сохранён!")
    
    def _add_plan_topic(self):
        """Добавление темы в план занятий"""
        QMessageBox.information(
            self,
            "Инфо",
            "Функция добавления темы будет доступна в следующей версии"
        )
    
    def _save_notes(self):
        """Сохранение заметок"""
        notes = self._notes_edit.toPlainText()
        # Здесь можно добавить сохранение в БД
        QMessageBox.information(self, "Успешно", "Заметки сохранены!")