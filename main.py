import os
import subprocess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

def update_ytdlp():
    try:
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'], check=True)
    except Exception:
        pass

update_ytdlp()

TOKEN = '8749124006:AAGSJv3WCle4K_H3f089dKoywY4Rsd9yOD0'
bot = telebot.TeleBot(TOKEN)

telebot.apihelper.CONNECT_TIMEOUT = 300
telebot.apihelper.READ_TIMEOUT = 300

try:
    bot.remove_webhook()
except Exception:
    pass

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

user_links = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to all in one video downloader we can download audio and video from any platform link and thank you for using all in one video downloader")

@bot.message_handler(func=lambda message: message.text and message.text.startswith("http"))
def handle_link(message):
    user_id = message.from_user.id
    user_links[user_id] = message.text
    chat_id = message.chat.id
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Download Video', callback_data='dl_video'),
        InlineKeyboardButton('Download MP3 (Audio)', callback_data='dl_audio')
    )
    bot.send_message(chat_id, "What would you like to download?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    if user_id not in user_links:
        bot.answer_callback_query(call.id, "Link expired or not found. Please send the link again.")
        return
        
    url = user_links[user_id]
    chat_id = call.message.chat.id
    
    if call.data == 'dl_video':
        bot.send_message(chat_id, "Downloading video...")
        ydl_opts = {
            'format': 'bestvideo[height<=1000][filesize<200M]+bestaudio/best/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            bot.send_message(chat_id, "Uploading video by ayush")
            with open(filename, 'rb') as video:
                bot.send_video(chat_id, video)
            os.remove(filename)
        except Exception as e:
            bot.send_message(chat_id, f"Error: {e}")

    elif call.data == 'dl_audio':
        bot.send_message(chat_id, "Downloading audio...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            base, _ = os.path.splitext(filename)
            audio_file = base + '.mp3'
            
            bot.send_message(chat_id, "Uploading audio by ayush")
            with open(audio_file, 'rb') as audio:
                bot.send_audio(chat_id, audio)
            os.remove(audio_file)
        except Exception as e:
            bot.send_message(chat_id, f"Error: {e}")

bot.infinity_polling(skip_pending=True)
    
