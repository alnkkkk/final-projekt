
import sqlite3 # импотируем библиотеку для работы с базой данных SQLite
from pathlib import Path # импотируем класс Path для удобной работы с путями к файлам
from typing import Tuple, List  #Импортируем классы Tuple и List для улучшения читабельности и документации функций

DB_PATH = Path("history.db") # Устанавливаем путь к файлу базы данных SQLite (название файла history.db)



def get_connection(): # Объявление функции для получения соединения с базой данных
    return sqlite3.connect(DB_PATH) # Открываем соединение с базой данных, указанной в DB_PATH


def init_db() -> None: # Функция инициализации базы данных (создание таблиц)
    conn = get_connection() # Получаем соединение с базой данных
    cur = conn.cursor()   # Создаем курсор для выполнения SQL-команд
    cur.execute(
        """CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            movie_id TEXT,
            rating REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()  #Применяем изменения в базе данных
    conn.close()     # Закрываем соединение с базой данных


def save_request(user_id: int, username: str, movie_id: str, rating: float) -> None: # Функция для сохранения нового запроса
    conn = get_connection() # Открываем новое соединение с базой данных
    cur = conn.cursor() # Создаем курсор для выполнения SQL-запросов
    cur.execute(
        """INSERT INTO requests(user_id, username, movie_id, rating)
        VALUES (?, ?, ?, ?)""",
        (user_id, username, movie_id, rating),  # Передаем аргументы (значения полей) в запрос
    )
    conn.commit() # Применяем изменения в базе данных
    conn.close()  # Закрываем соединение с базой данных


def get_stats() -> Tuple[int, List[tuple]]:  # Функция для получения общей статистики и популярных фильмов
    conn = get_connection()  # Открываем новое соединение с базой данных
    cur = conn.cursor()  # Создаем курсор для выполнения SQL-запросов
    cur.execute("SELECT COUNT(*) FROM requests") # Запрашиваем общее количество записей в таблице
    total = cur.fetchone()[0] or 0 # Получаем первое значение результата (количество записей

    cur.execute( # Выполняем SQL-запрос для выбора пяти наиболее часто встречающихся фильмов
        """SELECT movie_id, COUNT(*) AS c
        FROM requests
        GROUP BY movie_id
        ORDER BY c DESC
        LIMIT 5"""
    )
    rows = cur.fetchall()  # Получаем все строки результатов (топ-5 фильмов)
    conn.close()  # Закрываем соединение с базой данных

    # movie_id -> title lookup is not stored; just show id and count
    top = [(f"ID {mid}", cnt) for (mid, cnt) in rows] # Форматируем полученные данные в удобный вид
    return total, top  # Возвращаем общий счётчик и список популярных фильмов
