import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = "8451279244:AAEnK50Qj0srjkW_dN5-KngHCBvJIQP3GX4"
TMDB_API_KEY = "10b5dbf58eee4f65515a5b99e3134b22"
ADMIN_CHAT_ID = 1979872756
BASE_LINK = "https://newzbysms.com/?search="

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- GLOBAL VARIABLE FOR CUSTOM LINK ---
custom_link = None

# --- SEARCH FUNCTION ---
def search_movie_link(movie_name: str):
    search_query = "+".join(movie_name.strip().split())
    if custom_link:
        return custom_link
    return f"{BASE_LINK}{search_query}"

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Movie Search Bot Ready!\nबस movie का नाम bhejo!")

# --- SET LINK COMMAND (Admin Only) ---
async def set_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global custom_link
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ सिर्फ admin ही यह command चला सकता है.")
        return

    if context.args:
        custom_link = " ".join(context.args)
        await update.message.reply_text(f"✅ Custom link set: {custom_link}")
    else:
        await update.message.reply_text("❗ Usage: /setlink <your_custom_link>")

# --- RESET LINK COMMAND (Admin Only) ---
async def reset_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global custom_link
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ सिर्फ admin ही यह command चला सकता है.")
        return

    custom_link = None
    await update.message.reply_text("🔄 Custom link reset कर दिया गया है.")

# --- HANDLE USER MESSAGES ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    movie_name = update.message.text.strip()

    # Generate link
    final_link = search_movie_link(movie_name)

    # Send to user
    await update.message.reply_text(
        f"🔍 Movie: {movie_name}\n📥 Download Link: {final_link}"
    )

    # Notify admin
    msg = (
        f"👤 User: {user.full_name} (ID: {user.id})\n"
        f"🔎 Searched: {movie_name}\n"
        f"📤 Sent Link: {final_link}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

# --- MAIN ---
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlink", set_link))
    app.add_handler(CommandHandler("resetlink", reset_link))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    await app.run_polling()

# --- ENTRY POINT FIX ---
import asyncio
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e).startswith("This event loop is already running"):
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            loop.run_forever()
        else:
            raise
