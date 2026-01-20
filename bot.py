
import logging
import os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from kino_client import extract_kp_id, get_movie_info
from storage import init_db, save_request

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Привет! Я бот, который показывает рейтинг фильма на Кинопоиске.\n\n"
        "Пришли мне ссылку вида:\n"
        "https://www.kinopoisk.ru/film/535341/\n\n"
        "Команды:\n"
        "/start — начать\n"
        "/help — справка\n"
        "/stats — статистика запросов"
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


def format_movie_message(movie: dict) -> str:
    title = movie.get("title") or "Фильм"
    year = movie.get("year")
    rating = movie.get("rating")

    lines = [f"🎬 {title}" + (f" ({year})" if year else "")]
    if rating is not None:
        lines.append(f"⭐ Рейтинг Кинопоиска: {rating}")
        if rating >= 8.0:
            lines.append("🔥 Обязателен к просмотру")
        elif rating >= 6.0:
            lines.append("👍 Крепкий фильм")
        else:
            lines.append("🤷‍♂️ На любителя")
    else:
        lines.append("Рейтинг недоступен")

    return "\n".join(lines)


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    url = message.text.strip()

    await message.reply_text("⏳ Ищу информацию о фильме...")

    movie_id = extract_kp_id(url)
    if not movie_id:
        await message.reply_text(
            "❌ Похоже, это не ссылка на фильм Кинопоиска.\n"
            "Пришли, пожалуйста, полную ссылку вида:\n"
            "https://www.kinopoisk.ru/film/326/"
        )
        return

    movie = get_movie_info(movie_id)
    if not movie:
        await message.reply_text(
            "⚠️ Не удалось получить информацию о фильме.\n"
            "Возможно, сервис временно недоступен."
        )
        return

    # сохраняем статистику
    save_request(
        user_id=message.from_user.id,
        username=message.from_user.username,
        movie_id=movie_id,
        rating=movie.get("rating"),
    )

    text = format_movie_message(movie)

    keyboard = [
        [
            InlineKeyboardButton(
                "🔗 Открыть на Кинопоиске", url=movie.get("url")
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(text, reply_markup=reply_markup)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from storage import get_stats

    total, top_movies = get_stats()
    lines = [f"Всего запросов: {total}"]
    if top_movies:
        lines.append("\nТоп фильмов по запросам:")
        for title, count in top_movies:
            lines.append(f"• {title} — {count}")
    else:
        lines.append("Пока статистики нет — сделайте первые запросы 🙂")

    await update.message.reply_text("\n".join(lines))


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан в .env")

    init_db()

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
