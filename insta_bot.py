import telebot
from telebot import types
import instaloader
import os
import re

# Bot tokeningizni shu yerga qo'ying
BOT_TOKEN = '8993250142:AAE7PDqJSAhJcT8A0sXAs1fZmsZtIVZVC8k'
bot = telebot.TeleBot(BOT_TOKEN)

L = instaloader.Instaloader(
    download_pictures=True, 
    download_videos=True, 
    download_video_thumbnails=False,
    save_metadata=False,
    dirname_pattern="downloads"
)

# Chiroyli tugmalar (Keyboard) yaratish funksiyasi
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_info = types.KeyboardButton("ℹ️ Bot Haqida")
    btn_help = types.KeyboardButton("📥 Qanday yuklanadi?")
    markup.add(btn_info, btn_help)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 *Assalomu alaykum!*\n\n"
        "🚀 Men Instagram'dan rasm va videolarni (Reels/Post) yuklab beruvchi aqlli botman!\n\n"
        "👉 Menga shunchaki video yoki rasm *havolasini (linkini)* yuboring."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    url = message.text.strip()
    
    # Tugmalar bosilganda qaytariladigan javoblar
    if url == "ℹ️ Bot Haqida":
        bot.send_message(message.chat.id, "👤 *Dasturchi:* Shahriyor\n⚡ *Tezlik:* Maksimal\n🛡 *Xavfsizlik:* 100% kafolatlangan.\n\nHech qanday reklamalarsiz va cheklovlarsiz xizmat ko'rsatadi!", parse_mode="Markdown")
        return
    elif url == "📥 Qanday yuklanadi?":
        bot.send_message(message.chat.id, "1. Instagram ilovasiga kiring.\n2. Biror video yoki rasmning *'Copy Link'* (Havolani nusxalash) tugmasini bosing.\n3. O'sha silkkani menga jo'nating va bir necha soniya kuting! 🔥", parse_mode="Markdown")
        return

    # Havolani tekshirish
    if "instagram.com" not in url:
        bot.send_message(message.chat.id, "⚠️ *Xatolik:* Iltimos, faqat to'g'ri Instagram havolasini yuboring!", parse_mode="Markdown")
        return

    msg = bot.send_message(message.chat.id, "🔍 *Havola tekshirilmoqda va yuklanmoqda...* ⏳", parse_mode="Markdown")

    try:
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
        else:
            for f in os.listdir("downloads"):
                try: os.remove(os.path.join("downloads", f))
                except: pass

        if "/p/" in url or "/reels/" in url or "/reel/" in url:
            match = re.search(r'(?:p|reel|reels)/([A-Za-z0-9_-]+)', url)
            if not match:
                bot.edit_message_text("❌ Video ID-sini topib bo'lmadi.", message.chat.id, msg.message_id)
                return
                
            shortcode = match.group(1)
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target="downloads")
            
            files = os.listdir("downloads")
            video_sent = False

            for file in files:
                file_path = os.path.join("downloads", file)
                if file.endswith('.mp4'):
                    with open(file_path, 'rb') as video:
                        bot.send_video(message.chat.id, video, caption="✨ *Mana siz so'ragan video!* \n\n📥 @SizningBotUserName", parse_mode="Markdown")
                        video_sent = True
                elif file.endswith('.jpg') and not video_sent:
                    with open(file_path, 'rb') as photo:
                        bot.send_photo(message.chat.id, photo, caption="✨ *Mana siz so'ragan rasm!* \n\n📥 @SizningBotUserName", parse_mode="Markdown")
            
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ Faqat Post yoki Reels linkini yuboring.", message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"⚠️ *Yuklashda xatolik yuz berdi!*\nProfil yopiq (private) bo'lsa bot yuklay olmaydi.", message.chat.id, msg.message_id, parse_mode="Markdown")

print("Bot chiroyli ko'rinishda ishga tushdi...")
bot.infinity_polling()
