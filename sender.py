import logging
import requests
import urllib.parse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = "8451279244:AAEnK50Qj0srjkW_dN5-KngHCBvJIQP3GX4"
TMDB_API_KEY = "10b5dbf58eee4f65515a5b99e3134b22"
ADMIN_CHAT_ID = 1979872756  # Tumhara Telegram ID

# --- Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- TMDB Movie Search Function ---
def search_movie_tmdb(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "en-US"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            movie = data["results"][0]
            title = movie["title"]
            overview = movie["overview"]
            poster_path = movie["poster_path"]
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            return title, overview, poster_url
    return None, None, None

# --- /start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "User"
    welcome_message = f"🎬 Welcome {name}!\n\nKoi bhi movie ka naam bhejo aur main uska info dunga."
    await update.message.reply_text(welcome_message)

# --- Handle User Messages ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else user.first_name

    title, overview, poster_url = search_movie_tmdb(user_query)

    if title:
        # ✅ Custom link with your website
        encoded_title = urllib.parse.quote(title)
        custom_link = f"https://newzbysms.com/?search={encoded_title}"

        # 🎁 Message to user
        user_message = f"🎬 *{title}*\n\n📝 {overview}\n\n🔗 [Movie Link]({custom_link})"
        if poster_url:
            await update.message.reply_photo(photo=poster_url, caption=user_message, parse_mode='Markdown')
        else:
            await update.message.reply_text(user_message, parse_mode='Markdown')

        # 🔔 Notify admin
        admin_message = (
            f"👤 *User:* {username} (ID: `{user_id}`)\n"
            f"🔍 *Searched:* {user_query}\n"
            f"🎬 *Found:* {title}\n"
            f"🔗 *Link Sent:* {custom_link}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message, parse_mode='Markdown')

    else:
        await update.message.reply_text("❌ Movie not found. Try another title.")
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"❌ {username} ne '{user_query}' search kiya but movie nahi mili."
        )

# --- Main Function ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
