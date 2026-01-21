
import os # Импортируем модуль os для работы с переменными окружения
import re # Импортируем модуль re для работы с регулярными выражениями
from typing import Optional, Dict, Any # Импортируем типы данных для аннотаций типов

# Подключаем библиотеку requests для отправки HTTP-запросов

import requests
# Используем библиотеку dotenv для загрузки переменных окружения из файла .env
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()
# Получаем значение ключа API из переменной окружения KP_API_KEY
API_KEY = os.getenv("KP_API_KEY")

# Создаем заголовки для запросов к API Kinopoisk
HEADERS = {"X-API-KEY": API_KEY}
# Определяем базовый URL для API Kinopoisk
BASE_URL = "https://api.kinopoisk.dev/v1.4/movie"


# Функция для извлечения ID фильма из ссылки Кинопоиска
def extract_kp_id(url: str) -> Optional[str]:
    """Извлекает ID фильма из ссылки Кинопоиска."""
    # Регулярное выражение для поиска шаблона "/film/ID" или "/series/ID"
    m = re.search(r"/(film|series)/(\d+)", url)
    # Возвращаем вторую группу совпадения (ID), если найдено
    return m.group(2) if m else None

# Функция для получения информации о фильме по его ID
def get_movie_info(movie_id: str) -> Optional[Dict[str, Any]]:
    """Берём данные по фильму через kinopoisk.dev по ID."""
    if not API_KEY:
        return None
 # Отправляем GET-запрос к API с таймаутом 10 секунд
    try:
        resp = requests.get(f"{BASE_URL}/{movie_id}", headers=HEADERS, timeout=10)
    except requests.RequestException:
        # Если возникла ошибка при отправке запроса, возвращаем None
        return None      
     # Проверяем статус ответа сервера
    if resp.status_code != 200:
        return None
    
   # Преобразуем JSON-ответ в Python-словарь
    data = resp.json()
# Выбираем название фильма (оригинальное или альтернативное)
    title = (
        data.get("name")
        or data.get("alternativeName")
        or f"Фильм {movie_id}"
    )
     # Берем год выпуска фильма
    year = data.get("year")
    # Получаем блок рейтинга
    rating_block = data.get("rating") or {}
     # Выбираем рейтинг КП или IMDB
    rating = rating_block.get("kp") or rating_block.get("imdb")
    # Если рейтинг отсутствует, возвращаем None
    if rating is None:
        return None
 # Пробуем преобразовать рейтинг в число
    try:
        rating_value = float(rating)
    except (TypeError, ValueError):
        return None
#формируем итоговый словарь с информацией о фильме 
    return {
        "title": title,    # назание фильма 
        "year": year,      # год выпуска
        "rating": rating_value,    # Рейтинг фильма 
        "url": f"https://www.kinopoisk.ru/film/{movie_id}/",
    }
