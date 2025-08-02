import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Bot and API Keys
TELEGRAM_BOT_TOKEN = "8451279244:AAEnK50Qj0srjkW_dN5-KngHCBvJIQP3GX4"
TMDB_API_KEY = "10b5dbf58eee4f65515a5b99e3134b22"
ADMIN_CHAT_ID = 1979872756
BASE_URL = "https://newzbysms.com"

# Logging
logging.basicConfig(level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Koi bhi movie ka naam bhejiye aur main aapko uska link dunga!")

# Search handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user = update.message.from_user
    user_name = user.first_name
    user_username = user.username or "No username"

    # Search Movie in TMDB
    response = requests.get(
        f"https://api.themoviedb.org/3/search/movie",
        params={"api_key": TMDB_API_KEY, "query": user_input}
    )

    data = response.json()
    if data["results"]:
        movie = data["results"][0]
        title = movie["title"]
        movie_url = f"{BASE_URL}/?movie={title.replace(' ', '-')}"

        # Message to User
        await update.message.reply_text(f"🎬 *{title}*\n📥 Download Link: {movie_url}", parse_mode="Markdown")

        # Message to Admin
        admin_msg = (
            f"🧑‍💻 User: {user_name} (@{user_username})\n"
            f"🔍 Searched: {title}\n"
            f"🔗 Link: {movie_url}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)
    else:
        await update.message.reply_text("❌ Movie not found. Please try another title.")

# Main App
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
