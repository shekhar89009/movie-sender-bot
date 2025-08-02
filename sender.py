import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Setup
TELEGRAM_BOT_TOKEN = "8451279244:AAEnK50Qj0srjkW_dN5-KngHCBvJIQP3GX4"
TMDB_API_KEY = "10b5dbf58eee4f65515a5b99e3134b22"
ADMIN_CHAT_ID = 1979872756
BASE_URL = "https://newzbysms.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Movie Search Bot Me Welcome! Koi bhi movie ka naam bhejo.")

# Search & respond
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    user_id = update.message.chat.id

    # Call TMDB API
    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={user_query}"
    response = requests.get(tmdb_url).json()
    results = response.get("results")

    if not results:
        await update.message.reply_text("❌ Movie nahi mili. Dusra naam try karo.")
        return

    # Use first result
    movie = results[0]
    title = movie.get("title")
    movie_id = movie.get("id")
    overview = movie.get("overview", "No description.")
    movie_link = f"{BASE_URL}/movie/{movie_id}"

    # User response
    reply_text = f"🎬 *{title}*\n\n📝 {overview}\n\n🔗 [Watch/Download Here]({movie_link})"
    await update.message.reply_markdown(reply_text)

    # Notify admin
    admin_text = f"👤 User: `{user_id}`\n🔎 Search: *{user_query}*\n🎬 Found: {title}\n🔗 Link: {movie_link}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="Markdown")

# Main function
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot Running...")
    await app.run_polling()

# Entry point
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
