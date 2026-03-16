"""
Kairos Tutor - Работа с базой данных
Использует Config для безопасного получения путей
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple

from core.config import config
from utils.helpers import generate_student_uuid


class Database:
    """
    Класс для работы с SQLite базой данных.
    
    Все приватные данные (пути, подключения) используют префикс _.
    """
    
    _instance: Optional['Database'] = None
    
    def __new__(cls):
        """Singleton паттерн для базы данных"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Приватные переменные
        self._conn = None
        self._cursor = None
        
        # Получение пути из конфигурации
        self._db_path = config.db_full_path
        
        self._connect()
        self._initialized = True
    
    def _connect(self):
        """Подключение к базе данных (приватный метод)"""
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()
    
    def create_tables(self):
        """Создание таблиц если они не существуют"""
        # Таблица учеников
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_uuid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица уроков
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                scheduled_date DATE,
                recurrence_type TEXT DEFAULT 'none',
                status TEXT DEFAULT 'scheduled',
                notes TEXT,
                grade TEXT,
                completed_at DATETIME,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)
        
        # Таблица планов занятий
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                is_completed BOOLEAN DEFAULT 0,
                order_num INTEGER DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)
        
        # Таблица результатов (для графика успеваемости)
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER,
                student_id INTEGER NOT NULL,
                grade TEXT,
                date DATE,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)
        
        self._conn.commit()
    
    # ============================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С УЧЕНИКАМИ
    # ============================================
    
    def get_all_students(self) -> List[sqlite3.Row]:
        """Получение всех учеников"""
        self._cursor.execute("SELECT * FROM students ORDER BY name")
        return self._cursor.fetchall()
    
    def search_students(self, query: str) -> List[sqlite3.Row]:
        """Поиск учеников по имени или ID"""
        self._cursor.execute("""
            SELECT * FROM students 
            WHERE name LIKE ? OR student_uuid LIKE ?
            ORDER BY name
        """, (f"%{query}%", f"%{query}%"))
        return self._cursor.fetchall()
    
    def get_student_by_id(self, student_id: int) -> Optional[sqlite3.Row]:
        """Получение ученика по ID"""
        self._cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        return self._cursor.fetchone()
    
    def get_student_by_uuid(self, student_uuid: str) -> Optional[sqlite3.Row]:
        """Получение ученика по UUID"""
        self._cursor.execute("SELECT * FROM students WHERE student_uuid = ?", (student_uuid,))
        return self._cursor.fetchone()
    
    def add_student(self, name: str, student_uuid: Optional[str] = None) -> int:
        """
        Добавление нового ученика.
        
        Args:
            name: Имя ученика
            student_uuid: Уникальный ID (генерируется автоматически если не указан)
        
        Returns:
            int: ID нового ученика
        """
        if student_uuid is None:
            student_uuid = generate_student_uuid()
        
        self._cursor.execute("""
            INSERT INTO students (name, student_uuid)
            VALUES (?, ?)
        """, (name, student_uuid))
        self._conn.commit()
        return self._cursor.lastrowid
    
    def update_student(self, student_id: int, name: Optional[str] = None, 
                       status: Optional[str] = None) -> bool:
        """Обновление данных ученика"""
        updates = []
        values = []
        
        if name is not None:
            updates.append("name = ?")
            values.append(name)
        
        if status is not None:
            updates.append("status = ?")
            values.append(status)
        
        if not updates:
            return False
        
        values.append(student_id)
        
        self._cursor.execute(f"""
            UPDATE students 
            SET {', '.join(updates)}
            WHERE id = ?
        """, values)
        self._conn.commit()
        return self._cursor.rowcount > 0
    
    def delete_student(self, student_id: int) -> bool:
        """Удаление ученика"""
        self._cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        self._conn.commit()
        return self._cursor.rowcount > 0
    
    # ============================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С УРОКАМИ
    # ============================================
    
    def get_lessons_by_student(self, student_id: int) -> List[sqlite3.Row]:
        """Получение всех уроков ученика"""
        self._cursor.execute("""
            SELECT * FROM lessons 
            WHERE student_id = ? 
            ORDER BY scheduled_date DESC
        """, (student_id,))
        return self._cursor.fetchall()
    
    def get_upcoming_lessons(self, student_id: int, limit: int = 5) -> List[sqlite3.Row]:
        """Получение предстоящих уроков ученика"""
        self._cursor.execute("""
            SELECT * FROM lessons 
            WHERE student_id = ? AND status = 'scheduled' AND scheduled_date >= date('now')
            ORDER BY scheduled_date ASC
            LIMIT ?
        """, (student_id, limit))
        return self._cursor.fetchall()
    
    def get_next_lesson(self, student_id: int) -> Optional[sqlite3.Row]:
        """Получение следующего урока ученика"""
        self._cursor.execute("""
            SELECT * FROM lessons 
            WHERE student_id = ? AND status = 'scheduled' AND scheduled_date >= date('now')
            ORDER BY scheduled_date ASC
            LIMIT 1
        """, (student_id,))
        return self._cursor.fetchone()
    
    def add_lesson(self, student_id: int, scheduled_date: str, 
                   recurrence_type: str = 'none', status: str = 'scheduled') -> int:
        """
        Добавление нового урока.
        
        Args:
            student_id: ID ученика
            scheduled_date: Дата урока (строка в формате YYYY-MM-DD)
            recurrence_type: Тип повторения ('none', 'weekly', 'biweekly', 'monthly')
            status: Статус урока
        
        Returns:
            int: ID нового урока
        """
        self._cursor.execute("""
            INSERT INTO lessons (student_id, scheduled_date, recurrence_type, status)
            VALUES (?, ?, ?, ?)
        """, (student_id, scheduled_date, recurrence_type, status))
        self._conn.commit()
        return self._cursor.lastrowid
    
    def update_lesson_status(self, lesson_id: int, status: str, 
                             notes: Optional[str] = None, 
                             grade: Optional[str] = None) -> bool:
        """
        Обновление статуса урока.
        
        Args:
            lesson_id: ID урока
            status: Новый статус ('completed', 'rescheduled', 'cancelled')
            notes: Заметки к уроку
            grade: Оценка
        
        Returns:
            bool: Успешность обновления
        """
        updates = ["status = ?"]
        values = [status]
        
        if notes is not None:
            updates.append("notes = ?")
            values.append(notes)
        
        if grade is not None:
            updates.append("grade = ?")
            values.append(grade)
        
        if status == 'completed':
            updates.append("completed_at = ?")
            values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        values.append(lesson_id)
        
        self._cursor.execute(f"""
            UPDATE lessons 
            SET {', '.join(updates)}
            WHERE id = ?
        """, values)
        self._conn.commit()
        return self._cursor.rowcount > 0
    
    def update_lesson_date(self, lesson_id: int, new_date: str) -> bool:
        """Перенос урока на новую дату"""
        self._cursor.execute("""
            UPDATE lessons 
            SET scheduled_date = ?, status = 'scheduled'
            WHERE id = ?
        """, (new_date, lesson_id))
        self._conn.commit()
        return self._cursor.rowcount > 0
    
    def delete_lesson(self, lesson_id: int) -> bool:
        """Удаление урока"""
        self._cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
        self._conn.commit()
        return self._cursor.rowcount > 0
    
    # ============================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ПЛАНАМИ ЗАНЯТИЙ
    # ============================================
    
    def get_study_plan(self, student_id: int) -> List[sqlite3.Row]:
        """Получение плана занятий ученика"""
        self._cursor.execute("""
            SELECT * FROM study_plans 
            WHERE student_id = ? 
            ORDER BY order_num ASC
        """, (student_id,))
        return self._cursor.fetchall()
    
    def add_plan_topic(self, student_id: int, topic: str, 
                       order_num: Optional[int] = None) -> int:
        """Добавление темы в план занятий"""
        if order_num is None:
            # Получаем следующий номер порядка
            self._cursor.execute("""
                SELECT MAX(order_num) FROM study_plans WHERE student_id = ?
            """, (student_id,))
            result = self._cursor.fetchone()
            order_num = (result[0] or 0) + 1
        
        self._cursor.execute("""
            INSERT INTO study_plans (student_id, topic, order_num)
            VALUES (?, ?, ?)
        """, (student_id, topic, order_num))
        self._conn.commit()
        return self._cursor.lastrowid
    
    def update_plan_topic(self, topic_id: int, is_completed: bool) -> bool:
        """Обновление статуса темы в плане"""
        self._cursor.execute("""
            UPDATE study_plans 
            SET is_completed = ?
            WHERE id = ?
        """, (1 if is_completed else 0, topic_id))
        self._conn.commit()
        return self._cursor.rowcount > 0
    
    def delete_plan_topic(self, topic_id: int) -> bool:
        """Удаление темы из плана"""
        self._cursor.execute("DELETE FROM study_plans WHERE id = ?", (topic_id,))
        self._conn.commit()
        return self._cursor.rowcount > 0
    
    def get_plan_progress(self, student_id: int) -> Tuple[int, int]:
        """
        Получение прогресса плана занятий.
        
        Returns:
            Tuple[int, int]: (выполнено, всего)
        """
        self._cursor.execute("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed
            FROM study_plans 
            WHERE student_id = ?
        """, (student_id,))
        result = self._cursor.fetchone()
        return (result['completed'] or 0, result['total'] or 0)
    
    # ============================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С РЕЗУЛЬТАТАМИ
    # ============================================
    
    def get_results_by_student(self, student_id: int) -> List[sqlite3.Row]:
        """Получение всех результатов ученика"""
        self._cursor.execute("""
            SELECT * FROM results 
            WHERE student_id = ? 
            ORDER BY date DESC
        """, (student_id,))
        return self._cursor.fetchall()
    
    def add_result(self, student_id: int, grade: str, 
                   date: Optional[str] = None, 
                   lesson_id: Optional[int] = None) -> int:
        """Добавление результата урока"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        self._cursor.execute("""
            INSERT INTO results (student_id, grade, date, lesson_id)
            VALUES (?, ?, ?, ?)
        """, (student_id, grade, date, lesson_id))
        self._conn.commit()
        return self._cursor.lastrowid
    
    def get_average_grade(self, student_id: int) -> Optional[float]:
        """Получение средней оценки ученика"""
        self._cursor.execute("""
            SELECT AVG(
                CASE 
                    WHEN grade IN ('5', 'отлично') THEN 5
                    WHEN grade IN ('4', 'хорошо') THEN 4
                    WHEN grade IN ('3', 'удовл.') THEN 3
                    WHEN grade IN ('2', 'неуд.') THEN 2
                    ELSE NULL
                END
            ) as avg_grade
            FROM results 
            WHERE student_id = ?
        """, (student_id,))
        result = self._cursor.fetchone()
        return result['avg_grade'] if result else None
    
    # ============================================
    # ОБЩИЕ МЕТОДЫ
    # ============================================
    
    def close(self):
        """Закрытие подключения к базе данных"""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None
    
    def __del__(self):
        """Деструктор для закрытия подключения"""
        self.close()