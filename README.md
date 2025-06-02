# Discord QA Bot

This bot listens to a Discord channel and answers questions based on recent message history using OpenAI GPT.

## Features

- Maintains a rolling history of the last N messages (default 50) using a SQLite database for persistence.
- When mentioned with a question, sends the recent message history and the question to OpenAI and returns the response.

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables:
   - `DISCORD_TOKEN` – your Discord bot token.
   - `OPENAI_API_KEY` – API key for OpenAI.
   - Optional: `HISTORY_LIMIT` (number of messages to keep, default 50) and `HISTORY_DB` (path to SQLite database).
3. Run the bot:
   ```bash
   python bot.py
   ```

The bot must have access to read message content in the desired channels for context collection.
