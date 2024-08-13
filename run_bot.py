from telegram import Update
from telegram.ext import *
import yt_dlp
import os
import json

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
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if info_dict:
                ydl.download([url])
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
            users = load_users()
            for user_id in users:
                try:
                    await context.bot.send_message(chat_id=user_id, text=message)
                except Exception as e:
                    print(f"Failed to send message to {user_id}: {e}")
        else:
            await update.message.reply_text("يرجى إدخال رسالة لإرسالها.")
    else:
        await update.message.reply_text("ليس لديك صلاحية استخدام هذا الأمر.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(API_KEY).build()

    # Handlers
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    user_count_handler = CommandHandler('user_count', get_user_count)
    start_handler = CommandHandler('start', start)
    broadcast_handler = CommandHandler('broadcast', broadcast)

    application.add_handler(text_handler)
    application.add_handler(user_count_handler)
    application.add_handler(start_handler)
    application.add_handler(broadcast_handler)

    application.run_polling()
