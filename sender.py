import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- API KEYS ---
TELEGRAM_BOT_TOKEN = "8451279244:AAEnK50Qj0srjkW_dN5-KngHCBvJIQP3GX4"
TMDB_API_KEY = "10b5dbf58eee4f65515a5b99e3134b22"
ADMIN_CHAT_ID = 1979872756

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Global Link Variable ---
custom_link_prefix = "https://newzbysms.com"

# --- Command to Set Custom Link (Only by Admin) ---
async def set_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global custom_link_prefix
    if update.effective_user.id == ADMIN_CHAT_ID:
        if context.args:
            new_link = context.args[0]
            custom_link_prefix = new_link
            await update.message.reply_text(f"✅ Custom link set to: {new_link}")
        else:
            await update.message.reply_text("❌ Usage: /setlink https://yourlink.com")
    else:
        await update.message.reply_text("❌ You are not authorized to set the link.")

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Welcome! Send me any movie name to search.")

# --- Search Movie and Respond ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global custom_link_prefix
    user_query = update.message.text
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    # TMDB API call
    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={user_query}"
    response = requests.get(tmdb_url)
    data = response.json()

    if data["results"]:
        movie = data["results"][0]
        movie_title = movie["title"]
        movie_id = movie["id"]
        movie_year = movie.get("release_date", "")[:4]

        final_link = f"{custom_link_prefix}/movie/{movie_id}"
        message_to_user = f"🎬 *{movie_title}* ({movie_year})\n🔗 [Download Link]({final_link})"
        await update.message.reply_markdown(message_to_user)

        # Notify admin
        admin_msg = (
            f"👤 User: {user_name} (ID: {user_id})\n"
            f"🔎 Searched for: {user_query}\n"
            f"📨 Link Sent: {final_link}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)
    else:
        await update.message.reply_text("❌ No results found.")

# --- Main ---
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlink", set_link))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Bot running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
