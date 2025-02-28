import os
import logging
from pyrogram import Client, filters
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", 0))  # Convert to integer
API_HASH = os.getenv("API_HASH")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Check if all required env variables are set
if not all([BOT_TOKEN, API_ID, API_HASH, YOUTUBE_API_KEY]):
    logger.error("Missing environment variables! Please set BOT_TOKEN, API_ID, API_HASH, and YOUTUBE_API_KEY.")
    exit(1)

# Initialize Telegram bot
bot = Client("yt_uploader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize YouTube API
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

@bot.on_message(filters.video & filters.private)
async def upload_video(client, message):
    try:
        video = message.video
        file_path = await message.download()

        await message.reply_text("📤 Uploading your video to YouTube...")

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "Uploaded via Telegram Bot",
                    "description": "Uploaded from Telegram using Python",
                    "tags": ["Telegram", "YouTube", "Bot"],
                    "categoryId": "22",
                },
                "status": {"privacyStatus": "public"},
            },
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True),
        )

        response = request.execute()
        video_id = response.get("id")

        await message.reply_text(f"✅ Video uploaded! Watch it here: https://youtu.be/{video_id}")

        # Remove the file after upload
        os.remove(file_path)

    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply_text(f"❌ Error uploading video: {str(e)}")

# Start the bot
bot.run()
