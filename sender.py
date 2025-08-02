import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = "8451279244:AAEnK50Qj0srjkW_dN5-KngHCBvJIQP3GX4"
TMDB_API_KEY = "10b5dbf58eee4f65515a5b99e3134b22"
ADMIN_CHAT_ID = 1979872756
BASE_URL = "https://newzbysms.com"  # You can change this via admin command

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- TMDB SEARCH FUNCTION ---
def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    data = response.json()
    if data.get("results"):
        movie = data["results"][0]
        title = movie.get("title", "No Title")
        movie_id = movie.get("id")
        return title, f"{BASE_URL}/movie/{movie_id}"
    else:
        return None, None

# --- /start handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Welcome! Send any movie name to search it.")

# --- movie search handler ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    query = update.message.text
    title, link = search_movie(query)

    if title and link:
        message = f"🔎 *You searched:* {query}\n🎬 *Found:* {title}\n🔗 *Download:* {link}"
        await update.message.reply_text(message, parse_mode="Markdown")

        # Notify admin
        admin_msg = (
            f"👤 User: {user.first_name} ({user.id})\n"
            f"🔍 Searched: {query}\n"
            f"📎 Link Sent: {link}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)
    else:
        await update.message.reply_text("❌ Movie not found. Try something else!")

# --- Admin command to update link base ---
async def setbase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BASE_URL
    user = update.message.from_user

    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ You're not authorized.")
        return

    if context.args:
        BASE_URL = context.args[0]
        await update.message.reply_text(f"✅ Base link updated to: {BASE_URL}")
    else:
        await update.message.reply_text("❗ Usage: /setbase https://yourdomain.com")

# --- MAIN FUNCTION ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setbase", setbase))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
