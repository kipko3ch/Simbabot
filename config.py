from pyrogram import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the values from the environment
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# Initialize the Telegram Client
app = Client("mining_app", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Example usage (start the bot)
if __name__ == "__main__":
    app.run()