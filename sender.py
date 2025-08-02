import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = "8451279244:AAEnK50Qj0srjkW_dN5-KngHCBvJIQP3GX4"
TMDB_API_KEY = "10b5dbf58eee4f65515a5b99e3134b22"
ADMIN_CHAT_ID = 1979872756
base_link = "https://newzbysms.com"  # Default link

# --- LOGGER ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- STORE LINK (Changeable by admin) ---
dynamic_link = {"url": base_link}

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Welcome! Type any movie name to search.")

# --- ADMIN: Change link command ---
async def setlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return

    if context.args:
        new_link = context.args[0]
        dynamic_link["url"] = new_link
        await update.message.reply_text(f"✅ Link updated to: {new_link}")
    else:
        await update.message.reply_text("❗ Usage: /setlink https://yourlink.com")

# --- MAIN SEARCH HANDLER ---
async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    user_id = update.effective_chat.id

    # Search TMDB
    response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={user_query}")
    data = response.json()

    if data["results"]:
        title = data["results"][0]["title"]
        movie_id = data["results"][0]["id"]

        # Create download link
        link = f"{dynamic_link['url']}/?movie={movie_id}"

        # Send to user
        await update.message.reply_text(f"🎥 *{title}*\n🔗 Download link: {link}", parse_mode="Markdown")

        # Send info to admin
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"🔍 *User:* `{user_id}` searched for: *{user_query}*\n"
                f"📤 Link sent: {link}"
            ),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Movie not found!")

# --- MAIN FUNCTION ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlink", setlink))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))

    logger.info("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
