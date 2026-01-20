
import sqlite3
from pathlib import Path
from typing import Tuple, List

DB_PATH = Path("history.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
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
    conn.commit()
    conn.close()


def save_request(user_id: int, username: str, movie_id: str, rating: float) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO requests(user_id, username, movie_id, rating)
        VALUES (?, ?, ?, ?)""",
        (user_id, username, movie_id, rating),
    )
    conn.commit()
    conn.close()


def get_stats() -> Tuple[int, List[tuple]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM requests")
    total = cur.fetchone()[0] or 0

    cur.execute(
        """SELECT movie_id, COUNT(*) AS c
        FROM requests
        GROUP BY movie_id
        ORDER BY c DESC
        LIMIT 5"""
    )
    rows = cur.fetchall()
    conn.close()

    # movie_id -> title lookup is not stored; just show id and count
    top = [(f"ID {mid}", cnt) for (mid, cnt) in rows]
    return total, top
