import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
FOLDER_TOILET = os.environ.get("FOLDER_TOILET", "")
FOLDER_GENSET = os.environ.get("FOLDER_GENSET", "")
FOLDER_MFK = os.environ.get("FOLDER_MFK", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
CHAT_ID = int(os.environ.get("CHAT_ID", "0"))
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS", "")
PORT = int(os.environ.get("PORT", "8080"))
