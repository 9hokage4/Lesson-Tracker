"""
Kairos Tutor - График успеваемости
Виджет для визуализации оценок ученика
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFontMetrics


class GradeChart(QWidget):
    """
    Виджет для отображения графика успеваемости ученика.
    
    Рисует столбчатую диаграмму оценок с использованием QPainter.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Приватные переменные
        self._grades = []  # Список оценок (числа 2-5)
        self._labels = []  # Список меток (даты или номера уроков)
        self._max_height = 150
        self._bar_width = 40
        self._bar_spacing = 10
        
        # Цвета для оценок из палитры
        self._grade_colors = {
            5: QColor("#00AC6B"),   # Зелёный
            4: QColor("#408DD2"),   # Синий
            3: QColor("#F39C12"),   # Оранжевый
            2: QColor("#E74C3C"),   # Красный
        }
        
        self.setFixedHeight(self._max_height + 40)
    
    def set_grades(self, grades: list, labels: list = None):
        """
        Установка данных для графика.
        
        Args:
            grades: Список оценок (числа 2-5 или строки)
            labels: Список меток (даты, номера уроков)
        """
        self._grades = []
        for grade in grades:
            try:
                self._grades.append(int(grade))
            except (ValueError, TypeError):
                self._grades.append(3)  # По умолчанию 3
        
        self._labels = labels if labels else [f"Урок {i+1}" for i in range(len(grades))]
        
        # Обновление размера виджета
        self._update_size()
        self.update()
    
    def _update_size(self):
        """Обновление размера виджета на основе количества оценок"""
        num_grades = len(self._grades)
        if num_grades > 0:
            width = num_grades * (self._bar_width + self._bar_spacing) + self._bar_spacing
            self.setFixedWidth(max(200, min(600, width)))
    
    def paintEvent(self, event):
        """Отрисовка графика"""
        super().paintEvent(event)
        
        if not self._grades:
            self._draw_empty_state()
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Параметры отрисовки
        margin_left = 40
        margin_bottom = 30
        chart_height = self._max_height
        
        # Рисуем оси
        self._draw_axes(painter, margin_left, margin_bottom, chart_height)
        
        # Рисуем столбцы оценок
        self._draw_bars(painter, margin_left, margin_bottom, chart_height)
        
        # Рисуем метки
        self._draw_labels(painter, margin_left, margin_bottom)
    
    def _draw_axes(self, painter, margin_left, margin_bottom, chart_height):
        """Отрисовка осей координат"""
        pen = QPen(QColor("#043A6B"), 2)
        painter.setPen(pen)
        
        # Вертикальная ось
        start_x = margin_left
        start_y = 10
        end_y = self.height() - margin_bottom
        
        painter.drawLine(start_x, start_y, start_x, end_y)
        
        # Горизонтальная ось
        end_x = self.width() - 10
        painter.drawLine(start_x, end_y, end_x, end_y)
        
        # Метки на вертикальной оси (2, 3, 4, 5)
        painter.setFont(self.font())
        for i, grade in enumerate([2, 3, 4, 5]):
            y = end_y - ((i + 1) * chart_height / 5)
            painter.drawText(5, int(y + 5), str(grade))
            
            # Линии сетки
            grid_pen = QPen(QColor("#679FD2"), 1, Qt.PenStyle.DashLine)
            painter.setPen(grid_pen)
            painter.drawLine(start_x, int(y), end_x, int(y))
            painter.setPen(pen)
    
    def _draw_bars(self, painter, margin_left, margin_bottom, chart_height):
        """Отрисовка столбцов оценок"""
        num_grades = len(self._grades)
        if num_grades == 0:
            return
        
        bar_area_width = self.width() - margin_left - 10
        bar_width = min(self._bar_width, (bar_area_width - (num_grades - 1) * self._bar_spacing) // num_grades)
        
        for i, grade in enumerate(self._grades):
            # Позиция столбца
            x = margin_left + i * (bar_width + self._bar_spacing)
            
            # Высота столбца (пропорционально оценке)
            bar_height = (grade - 1) * chart_height / 5
            
            y = self.height() - margin_bottom - bar_height
            
            # Цвет столбца
            color = self._grade_colors.get(grade, QColor("#043A6B"))
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(110), 1))
            
            # Рисуем столбец со скруглением
            painter.drawRoundedRect(x, int(y), bar_width, int(bar_height), 5, 5)
    
    def _draw_labels(self, painter, margin_left, margin_bottom):
        """Отрисовка меток под столбцами"""
        num_grades = len(self._grades)
        if num_grades == 0:
            return
        
        bar_area_width = self.width() - margin_left - 10
        bar_width = min(self._bar_width, (bar_area_width - (num_grades - 1) * self._bar_spacing) // num_grades)
        
        painter.setPen(QPen(QColor("#043A6B"), 1))
        painter.setFont(self.font())
        
        for i, label in enumerate(self._labels[:10]):  # Максимум 10 меток
            x = margin_left + i * (bar_width + self._bar_spacing) + bar_width // 2
            y = self.height() - margin_bottom + 20
            
            # Обрезаем длинные метки
            if len(label) > 5:
                label = label[:5]
            
            painter.drawText(int(x - 15), int(y), 30, 20, Qt.AlignmentFlag.AlignCenter, label)
    
    def _draw_empty_state(self):
        """Отрисовка состояния когда нет данных"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setPen(QPen(QColor("#043A6B"), 1))
        painter.setFont(self.font())
        
        text = "Нет данных об оценках"
        rect = self.rect()
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def get_average_grade(self) -> float:
        """Получение средней оценки"""
        if not self._grades:
            return 0.0
        return sum(self._grades) / len(self._grades)
    
    def clear(self):
        """Очистка графика"""
        self._grades = []
        self._labels = []
        self.update()