
import os
import re
from typing import Optional, Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("KP_API_KEY")

HEADERS = {"X-API-KEY": API_KEY}
BASE_URL = "https://api.kinopoisk.dev/v1.4/movie"


def extract_kp_id(url: str) -> Optional[str]:
    """Извлекает ID фильма из ссылки Кинопоиска."""
    m = re.search(r"/(film|series)/(\d+)", url)
    return m.group(2) if m else None


def get_movie_info(movie_id: str) -> Optional[Dict[str, Any]]:
    """Берём данные по фильму через kinopoisk.dev по ID."""
    if not API_KEY:
        return None

    try:
        resp = requests.get(f"{BASE_URL}/{movie_id}", headers=HEADERS, timeout=10)
    except requests.RequestException:
        return None

    if resp.status_code != 200:
        return None

    data = resp.json()

    title = (
        data.get("name")
        or data.get("alternativeName")
        or f"Фильм {movie_id}"
    )
    year = data.get("year")

    rating_block = data.get("rating") or {}
    rating = rating_block.get("kp") or rating_block.get("imdb")
    if rating is None:
        return None

    try:
        rating_value = float(rating)
    except (TypeError, ValueError):
        return None

    return {
        "title": title,
        "year": year,
        "rating": rating_value,
        "url": f"https://www.kinopoisk.ru/film/{movie_id}/",
    }
