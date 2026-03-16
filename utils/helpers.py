"""
Kairos Tutor - Вспомогательные функции
Утилиты для генерации UUID, форматирования и других задач
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional


def generate_student_uuid() -> str:
    """
    Генерация уникального ID для ученика.
    
    Формат: STU-XXXXXX (где X - 6 символов)
    Пример: STU-A7B3C9
    
    Returns:
        str: Уникальный идентификатор ученика
    """
    # Генерируем случайный UUID и берём первые 6 символов
    unique_id = uuid.uuid4().hex[:6].upper()
    return f"STU-{unique_id}"


def format_date(date: datetime, format_string: str = "%d.%m.%Y") -> str:
    """
    Форматирование даты в строку.
    
    Args:
        date: Объект datetime для форматирования
        format_string: Формат строки (по умолчанию "%d.%m.%Y")
    
    Returns:
        str: Отформатированная дата
    """
    if date is None:
        return ""
    return date.strftime(format_string)


def parse_date(date_string: str, format_string: str = "%d.%m.%Y") -> Optional[datetime]:
    """
    Парсинг строки в дату.
    
    Args:
        date_string: Строка с датой
        format_string: Формат строки (по умолчанию "%d.%m.%Y")
    
    Returns:
        datetime или None если не удалось распарсить
    """
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, format_string)
    except ValueError:
        return None


def calculate_next_lesson_date(
    current_date: datetime,
    recurrence_type: str
) -> datetime:
    """
    Расчёт даты следующего урока на основе типа повторения.
    
    Args:
        current_date: Текущая дата урока
        recurrence_type: Тип повторения ('none', 'weekly', 'biweekly', 'monthly')
    
    Returns:
        datetime: Дата следующего урока
    """
    if recurrence_type == 'none':
        return current_date
    elif recurrence_type == 'weekly':
        return current_date + timedelta(weeks=1)
    elif recurrence_type == 'biweekly':
        return current_date + timedelta(weeks=2)
    elif recurrence_type == 'monthly':
        # Прибавляем месяц с обработкой граничных случаев
        month = current_date.month + 1
        year = current_date.year
        if month > 12:
            month = 1
            year += 1
        
        # Обрабатываем случаи когда день не существует в новом месяце (31->30)
        day = min(current_date.day, 
                  [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 
                   31, 31, 30, 31, 30, 31][month - 1])
        
        return current_date.replace(year=year, month=month, day=day)
    else:
        return current_date


def get_recurrence_options() -> list:
    """
    Получение списка опций повторения уроков.
    
    Returns:
        list: Список кортежей (отображаемое имя, значение для БД)
    """
    return [
        ("Не повторяется", "none"),
        ("Каждую неделю", "weekly"),
        ("Каждые 2 недели", "biweekly"),
        ("Каждый месяц", "monthly")
    ]


def get_lesson_status_options() -> list:
    """
    Получение списка статусов урока.
    
    Returns:
        list: Список кортежей (отображаемое имя, значение для БД)
    """
    return [
        ("Запланирован", "scheduled"),
        ("Проведён", "completed"),
        ("Перенесён", "rescheduled"),
        ("Отменён", "cancelled")
    ]


def get_student_status_options() -> list:
    """
    Получение списка статусов ученика.
    
    Returns:
        list: Список кортежей (отображаемое имя, значение для БД)
    """
    return [
        ("Активен", "active"),
        ("На паузе", "paused"),
        ("Архивирован", "archived")
    ]


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Обрезка текста до максимальной длины с добавлением многоточия.
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
    
    Returns:
        str: Обрезанный текст
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def calculate_progress(completed: int, total: int) -> int:
    """
    Расчёт прогресса в процентах.
    
    Args:
        completed: Количество завершённых элементов
        total: Общее количество элементов
    
    Returns:
        int: Процент прогресса (0-100)
    """
    if total == 0:
        return 0
    return int((completed / total) * 100)


def get_grade_color(grade: str) -> str:
    """
    Получение цвета для оценки.
    
    Args:
        grade: Оценка (5, 4, 3, 2 или текст)
    
    Returns:
        str: HEX код цвета
    """
    grade_colors = {
        '5': '#00AC6B',      # Зелёный
        '4': '#408DD2',      # Синий
        '3': '#F39C12',      # Оранжевый
        '2': '#E74C3C',      # Красный
        '1': '#E74C3C',      # Красный
        'отлично': '#00AC6B',
        'хорошо': '#408DD2',
        'удовл.': '#F39C12',
        'неуд.': '#E74C3C'
    }
    return grade_colors.get(str(grade).lower(), '#043A6B')


def get_days_until(date: datetime) -> int:
    """
    Расчёт количества дней до указанной даты.
    
    Args:
        date: Целевая дата
    
    Returns:
        int: Количество дней (отрицательное если дата в прошлом)
    """
    if date is None:
        return 0
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = date.replace(hour=0, minute=0, second=0, microsecond=0) - today
    return delta.days