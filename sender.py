import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = "8451279244:AAEnK50Qj0srjkW_dN5-KngHCBvJIQP3GX4"
TMDB_API_KEY = "10b5dbf58eee4f65515a5b99e3134b22"
ADMIN_CHAT_ID = 1979872756
BASE_SITE_URL = "https://newzbysms.com"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Mujhe koi bhi movie ka naam bhejo aur main uska download link dunga.")

# --- HANDLE SEARCH ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    user = update.message.from_user

    # TMDB API call
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    data = response.json()

    if data.get("results"):
        movie = data["results"][0]
        title = movie.get("title", "No Title Found")

        # Create custom link
        safe_title = title.lower().replace(" ", "-")
        download_link = f"{BASE_SITE_URL}/download/{safe_title}"

        # Send to user
        user_message = f"🎬 *{title}*\n📥 [Download Link]({download_link})"
        await update.message.reply_markdown(user_message)

        # Notify admin
        admin_message = (
            f"👤 User: {user.first_name} (@{user.username or 'NoUsername'})\n"
            f"🔍 Searched: {query}\n"
            f"🎬 Found: {title}\n"
            f"📤 Link sent: {download_link}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

    else:
        await update.message.reply_text("❌ Sorry, koi movie nahi mili!")

# --- MAIN ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()
