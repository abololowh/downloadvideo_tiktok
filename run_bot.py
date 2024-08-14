from telegram import Update
from telegram.ext import *
import yt_dlp
import os
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

API_KEY = '7257917415:AAFiG2hzhrn8zvhf3VCfPCepi9Xcq6BiJ7M'
USER_DATA_FILE = 'users.json'

ADMIN_USER_ID = 167042775  # استبدل هذا بمعرف المستخدم الإداري الخاص بك

print("Bot started")

# Load user IDs from file
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return []

# Save user ID to file
def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(users, file)

# Download video function
async def download_video(url: str) -> str:
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
    }
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = await loop.run_in_executor(pool, lambda: ydl.extract_info(url, download=False))
                if info_dict:
                    await loop.run_in_executor(pool, lambda: ydl.download([url]))
                    return 'video.mp4'
        except yt_dlp.utils.DownloadError:
            return None

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    save_user(user_id)  # Save user ID
    
    url = str(update.message.text)
    if url:
        await update.message.reply_text('جاري التحقق من صحة الرابط...')
        file_path = await download_video(url)
        if file_path:
            await update.message.reply_text('جاري تحميل الفيديو...')
            try:
                await update.message.reply_video(video=open(file_path, 'rb'))
                os.remove(file_path)
            except Exception as e:
                await update.message.reply_text(f'خطأ: {e}')
        else:
            await update.message.reply_text('تأكد من صحة الرابط.')

# Command to get the number of users
async def get_user_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_count = len(users)
    await update.message.reply_text(f'عدد المستخدمين: {user_count}')

# Command to start the bot and show number of users
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_count = len(users)
    welcome_message = (
        f"مرحبا! عدد المستخدمين الحاليين هو: {user_count}\n"
        "استخدم البوت لتحميل الفيديوهات."
    )
    await update.message.reply_text(welcome_message)

# Command to broadcast a message to all users (admin only)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == ADMIN_USER_ID:  # Ensure only admin can send broadcast
        if len(update.message.text.split(' ', 1)) > 1:
            message = update.message.text.split(' ', 1)[1]  # Get the message text after the command

