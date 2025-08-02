# sender.py

import logging
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))  # make sure it's numeric
BASE_URL = "https://newzbysms.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Welcome! Send a movie name.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user = update.message.from_user
    user_name = user.first_name
    user_username = user.username or "No username"

    response = requests.get(
        "https://api.themoviedb.org/3/search/movie",
        params={"api_key": TMDB_API_KEY, "query": user_input}
    )
    data = response.json()

    if not data.get("results"):
        await update.message.reply_text("❌ Movie not found.")
        return

    movie = data["results"][0]
    title = movie.get("title", "Unknown")
    overview = movie.get("overview", "No description.")
    poster_path = movie.get("poster_path")
    movie_url = f"{BASE_URL}/?movie={title.replace(' ', '-')}"

    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

    caption = (
        f"🎬 *{title}*\n"
        f"📝 {overview}\n"
        f"📥 [Download]({movie_url})"
    )

    if poster_url:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=poster_url, caption=caption, parse_mode="Markdown")
    else:
        await update.message.reply_text(caption, parse_mode="Markdown")

    admin_msg = (
        f"🧑‍💻 User: {user_name} (@{user_username})\n"
        f"🔍 Searched: {title}\n"
        f"🔗 Link: {movie_url}"
    )

    if poster_url:
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=poster_url, caption=admin_msg)
    else:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
