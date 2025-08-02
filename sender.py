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
        overview = movie.get("overview", "No description available.")
        poster_path = movie.get("poster_path")
        movie_url = f"{BASE_URL}/?movie={title.replace(' ', '-')}"

        # Poster Image URL
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            poster_url = None

        # Caption for User
        user_caption = (
            f"🎬 *{title}*\n"
            f"📝 {overview}\n"
            f"📥 [Download Now]({movie_url})"
        )

        # Send to User
        if poster_url:
            await context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=poster_url,
                caption=user_caption,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(user_caption, parse_mode="Markdown")

        # Send to Admin
        admin_msg = (
            f"🧑‍💻 User: {user_name} (@{user_username})\n"
            f"🔍 Searched: {title}\n"
            f"🔗 Link: {movie_url}"
        )

        if poster_url:
            await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=poster_url, caption=admin_msg)
        else:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)

    else:
        await update.message.reply_text("❌ Movie not found. Please try another title.")
