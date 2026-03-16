"""
Kairos Tutor - Главное окно приложения
Отображает сетку карточек учеников с поиском по имени и ID
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea, QGridLayout,
    QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.student_card import StudentCard
from ui.add_student_dialog import AddStudentDialog
from ui.student_profile import StudentProfileDialog


class MainWindow(QMainWindow):
    """Главное окно приложения с сеткой карточек учеников"""
    
    # Сигнал для обновления списка учеников
    students_updated = pyqtSignal()
    
    def __init__(self, database):
        super().__init__()
        
        # Приватные переменные
        self._db = database
        self._student_cards = []
        self._cards_per_row = 3
        
        # Настройка основного окна
        self._setup_window()
        
        # Создание центрального виджета
        self._central_widget = QWidget()
        self._central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self._central_widget)
        
        # Главный layout
        self._main_layout = QVBoxLayout(self._central_widget)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(20)
        
        # Верхняя панель (поиск + кнопка добавления)
        self._setup_top_panel()
        
        # Область с карточками учеников
        self._setup_students_grid()
        
        # Загрузка списка учеников
        self._load_students()
        
        # Подключение сигналов
        self.students_updated.connect(self._load_students)
    
    def _setup_window(self):
        """Настройка основного окна"""
        self.setWindowTitle("Kairos Tutor")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Установка шрифта по умолчанию
        font = QFont("Segoe UI", 12)
        self.setFont(font)
    
    def _setup_top_panel(self):
        """Создание верхней панели с поиском и кнопкой добавления"""
        self._top_panel = QWidget()
        self._top_panel_layout = QHBoxLayout(self._top_panel)
        
        # ✅ Layout margins (это логика, оставляем в Python)
        self._top_panel_layout.setContentsMargins(10, 10, 10, 10)
        self._top_panel_layout.setSpacing(15)
        
        # Поле поиска
        self._search_input = QLineEdit()
        self._search_input.setObjectName("searchInput")
        self._search_input.setPlaceholderText("🔍 Поиск по имени или ID ученика...")
        self._search_input.textChanged.connect(self._filter_students)
        
        # Кнопка добавления ученика
        self._add_button = QPushButton("+ Добавить ученика")
        self._add_button.setObjectName("primaryButton")
        self._add_button.clicked.connect(self._open_add_student_dialog)
        
        self._top_panel_layout.addWidget(self._search_input, stretch=1)
        self._top_panel_layout.addWidget(self._add_button)
        
        self._main_layout.addWidget(self._top_panel)
    
    def _setup_students_grid(self):
        """Создание сетки для карточек учеников"""
        # Контейнер для скролла
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setObjectName("studentsScrollArea")
        
        # Виджет-контейнер для карточек
        self._cards_container = QWidget()
        self._cards_layout = QGridLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(20)
        
        self._scroll_area.setWidget(self._cards_container)
        self._main_layout.addWidget(self._scroll_area, stretch=1)
    
    def _load_students(self):
        """Загрузка всех учеников из базы данных"""
        # Очистка текущих карточек
        self._clear_cards()
        
        # Получение данных из БД
        students = self._db.get_all_students()
        
        # Создание карточек для каждого ученика
        for index, student in enumerate(students):
            self._create_student_card(student, index)
        
        # Если учеников нет, показать заглушку
        if not students:
            self._show_empty_state()
    
    def _clear_cards(self):
        """Очистка всех карточек из сетки"""
        for card in self._student_cards:
            card.deleteLater()
        self._student_cards.clear()
        
        # Удаление заглушки если есть
        empty_label = self._cards_container.findChild(QLabel, "emptyLabel")
        if empty_label:
            empty_label.deleteLater()
    
    def _create_student_card(self, student_data, index):
        """Создание карточки ученика и добавление в сетку"""
        card = StudentCard(student_data)
        card.clicked.connect(self._open_student_profile)
        
        # Расчёт позиции в сетке
        row = index // self._cards_per_row
        col = index % self._cards_per_row
        
        self._cards_layout.addWidget(card, row, col)
        self._student_cards.append(card)
    
    def _show_empty_state(self):
        """Отображение сообщения когда нет учеников"""
        empty_label = QLabel(
            "Нет учеников\nНажмите «Добавить ученика» чтобы начать"
        )
        empty_label.setObjectName("emptyLabel")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._cards_layout.addWidget(
            empty_label, 0, 0, 1, self._cards_per_row
        )
    
    def _filter_students(self, search_text):
        """Фильтрация учеников по поисковому запросу"""
        search_text = search_text.strip()
        
        # Если поиск пустой - показать всех
        if not search_text:
            self._load_students()
            return
        
        # Поиск в БД (по имени или ID)
        students = self._db.search_students(search_text)
        
        # Очистка и обновление карточек
        self._clear_cards()
        
        for index, student in enumerate(students):
            self._create_student_card(student, index)
        
        # Если ничего не найдено
        if not students:
            self._show_not_found_state()
    
    def _show_not_found_state(self):
        """Отображение сообщения когда ничего не найдено"""
        empty_label = QLabel("Ученики не найдены\nПопробуйте другой запрос")
        empty_label.setObjectName("emptyLabel")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._cards_layout.addWidget(
            empty_label, 0, 0, 1, self._cards_per_row
        )
    
    def _open_add_student_dialog(self):
        """Открытие диалога добавления нового ученика"""
        dialog = AddStudentDialog(self._db, self)
        dialog.student_added.connect(self.students_updated.emit)
        dialog.exec()
    
    def _open_student_profile(self, student_id):
        """Открытие профиля ученика"""
        student_data = self._db.get_student_by_id(student_id)
        
        if student_data:
            dialog = StudentProfileDialog(student_data, self._db, self)
            dialog.lesson_updated.connect(self.students_updated.emit)
            dialog.exec()
    
    def resizeEvent(self, event):
        """Пересчёт количества карточек в ряд при изменении размера окна"""
        super().resizeEvent(event)
        
        # Адаптивное количество карточек в ряд
        width = self.width()
        
        if width < 800:
            self._cards_per_row = 1
        elif width < 1200:
            self._cards_per_row = 2
        else:
            self._cards_per_row = 3
        
        # Перерисовка сетки
        self._load_students()