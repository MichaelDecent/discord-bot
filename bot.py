import os
import discord
import openai
import aiosqlite
from collections import deque

HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", 50))
DB_PATH = os.getenv("HISTORY_DB", "history.db")

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions based on the following Discord conversation history."
)

class QuestionBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = deque(maxlen=HISTORY_LIMIT)
        self.db = None
        self.loop.create_task(self.setup_db())

    async def setup_db(self):
        self.db = await aiosqlite.connect(DB_PATH)
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, content TEXT)"
        )
        await self.db.commit()
        async with self.db.execute(
            "SELECT author, content FROM messages ORDER BY id DESC LIMIT ?",
            (HISTORY_LIMIT,),
        ) as cursor:
            rows = await cursor.fetchall()
            for author, content in reversed(rows):
                self.history.append({"author": author, "content": content})

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        self.history.append({"author": message.author.display_name, "content": message.content})
        if self.db is not None:
            await self.db.execute(
                "INSERT INTO messages(author, content) VALUES (?, ?)",
                (message.author.display_name, message.content),
            )
            await self.db.commit()

        if self.user.mentioned_in(message):
            mention_id = f"<@{self.user.id}>"
            mention_id_nick = f"<@!{self.user.id}>"
            question = (
                message.content.replace(mention_id, "").replace(mention_id_nick, "").strip()
            )
            if not question:
                return
            history_text = "\n".join(
                f"{m['author']}: {m['content']}" for m in self.history
            )
            user_prompt = f"{history_text}\nUser question: {question}"
            try:
                openai.api_key = os.getenv("OPENAI_API_KEY")
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                answer = response["choices"][0]["message"]["content"].strip()
            except Exception:
                answer = "Sorry, I couldn't generate a response right now."
            await message.channel.send(answer)

def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN environment variable is required")
    intents = discord.Intents.default()
    intents.message_content = True
    bot = QuestionBot(intents=intents)
    bot.run(token)

if __name__ == "__main__":
    main()
