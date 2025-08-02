import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = "8451279244:AAEnK50Qj0srjkW_dN5-KngHCBvJIQP3GX4"
TMDB_API_KEY = "10b5dbf58eee4f65515a5b99e3134b22"
ADMIN_CHAT_ID = 1979872756

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Global base URL (changeable by admin) ---
BASE_URL = "https://newzbysms.com"

# --- Command: /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Movie Bot Ready! Type any movie name to search.")

# --- Command: /seturl <new_url> ---
async def seturl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BASE_URL
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Access Denied. You are not the admin.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: /seturl https://yourwebsite.com")
        return

    BASE_URL = context.args[0]
    await update.message.reply_text(f"✅ Base URL updated to:\n{BASE_URL}")

# --- Handle movie search ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BASE_URL
    user_query = update.message.text
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={user_query}"
    response = requests.get(search_url)
    data = response.json()

    if not data.get("results"):
        await update.message.reply_text("❌ Movie not found.")
        return

    movie = data["results"][0]
    title = movie.get("title", "Unknown")
    year = movie.get("release_date", "????")[:4]

    # Create custom link with BASE_URL
    download_link = f"{BASE_URL}/?s={'+'.join(title.lower().split())}"

    # Send to user
    reply = f"🎬 *{title}* ({year})\n📥 [Download Now]({download_link})"
    await update.message.reply_markdown(reply)

    # Notify admin
    admin_msg = (
        f"📢 New Search Alert\n"
        f"👤 User: {user_name} (ID: {user_id})\n"
        f"🔍 Searched: {user_query}\n"
        f"📤 Link Sent: {download_link}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)

# --- Main ---
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("seturl", seturl))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    await app.run_polling()

# --- Entry Point ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
