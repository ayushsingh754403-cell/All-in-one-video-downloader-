import telebot
import yt_dlp
import os

TOKEN = '8749124006:AAFbyc9TAbKt8-O3XFWgAUppsMYBUFhn7eI'
bot = telebot.TeleBot(TOKEN)

# Temporary dictionary to store URL per user
user_urls = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Send me any video link, and I will give you options to download it as a Video or MP3 Audio.")

@bot.message_handler(func=lambda message: True)
def handle_url(message):
    url = message.text.strip()
    if not url.startswith("http"):
        bot.reply_to(message, "Please send a valid URL starting with http:// or https://")
        return
    
    # Save URL for this chat session
    user_urls[message.chat.id] = url
    
    # Create Inline Keyboard for Video and MP3 options
    markup = telebot.types.InlineKeyboardMarkup()
    btn_video = telebot.types.InlineKeyboardButton("📹 Download Video", callback_data="dl_video")
    btn_audio = telebot.types.InlineKeyboardButton("🎵 Download MP3", callback_data="dl_audio")
    markup.add(btn_video, btn_audio)
    
    bot.reply_to(message, "Link received! Choose your preferred format:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    url = user_urls.get(chat_id)
    
    if not url:
        bot.answer_callback_query(call.id, "Session expired. Please send the link again.")
        return

    if call.data == "dl_video":
        bot.answer_callback_query(call.id, "Downloading Video...")
        bot.edit_message_text("Please wait, downloading video...", chat_id, call.message.message_id)
        
        ydl_opts = {
            'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / best',
            'outtmpl': '%(id)s.%(ext)s',
            'noplaylist': True,
            'geo_bypass': True,
            'socket_timeout': 30,
        }
        
        downloaded_file = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                video_title = info.get('title', 'Downloaded Video')
            
            if downloaded_file and os.path.exists(downloaded_file):
                bot.edit_message_text(f"Uploading Video: {video_title}...", chat_id, call.message.message_id)
                
                # Custom caption with exact requested credit
                caption_text = f"{video_title}\n\n✨ Thank you for using Ayush All in One Video Downloader"
                
                with open(downloaded_file, 'rb') as video:
                    bot.send_video(chat_id, video, caption=caption_text)
                
                bot.delete_message(chat_id, call.message.message_id)
                os.remove(downloaded_file)
            else:
                bot.edit_message_text("Error: Video file could not be found.", chat_id, call.message.message_id)
        except Exception as e:
            bot.edit_message_text(f"Download failed: {str(e)[:100]}", chat_id, call.message.message_id)
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)

    elif call.data == "dl_audio":
        bot.answer_callback_query(call.id, "Downloading MP3...")
        bot.edit_message_text("Please wait, converting to MP3...", chat_id, call.message.message_id)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'geo_bypass': True,
            'socket_timeout': 30,
        }
        
        downloaded_file = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                base_filename = ydl.prepare_filename(info)
                downloaded_file = os.path.splitext(base_filename)[0] + '.mp3'
                audio_title = info.get('title', 'Downloaded Audio')
            
            if downloaded_file and os.path.exists(downloaded_file):
                bot.edit_message_text(f"Uploading MP3: {audio_title}...", chat_id, call.message.message_id)
                
                # Custom audio caption with exact requested credit
                caption_text = f"{audio_title}\n\n✨ Thank you for using Ayush All in One Video Downloader"
                
                with open(downloaded_file, 'rb') as audio:
                    bot.send_audio(chat_id, audio, caption=caption_text, title=audio_title)
                
                bot.delete_message(chat_id, call.message.message_id)
                os.remove(downloaded_file)
            else:
                bot.edit_message_text("Error: Audio file could not be found.", chat_id, call.message.message_id)
        except Exception as e:
            bot.edit_message_text(f"Download failed: {str(e)[:100]}", chat_id, call.message.message_id)
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)

if __name__ == '__main__':
    print("Bot is running and ready...")
    bot.polling()

