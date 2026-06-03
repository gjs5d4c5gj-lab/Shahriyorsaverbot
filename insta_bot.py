import telebot
import instaloader
import os
import re
import time

# 1. Telegram bot tokeningizni shu yerga yozing
BOT_TOKEN = '8993250142:AAE7PDqJSAhJcT8A0sXAs1fZmsZtIVZVC8k'
bot = telebot.TeleBot(BOT_TOKEN)

# Instaloader obyektini sozlaymiz
L = instaloader.Instaloader(
    download_pictures=True, 
    download_videos=True, 
    download_video_thumbnails=False,
    save_metadata=False,
    dirname_pattern="downloads"
)

# ⚠️ MUHIM ESLATMA (STORISLAR UCHUN):
# Instagram ochiq profildagi rasm va videolarni (Reels) login qilinmasa ham beradi.
# Lekin STORISLARNI yuklash uchun Instagram parolsiz ruxsat bermaydi.
# Agar storis ham yuklamoqchi bo'lsangiz, pastdagi 3 ta qator boshidagi # belgisini o'chirib, 
# o'zingizning feyk (qo'shimcha) instagram profilingiz logini va parolini yozib qo'ying:
# INSTA_USER = "instagram_loginingiz"
# INSTA_PASS = "instagram_parolingiz"
# L.login(INSTA_USER, INSTA_PASS)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga Instagram Post yoki Reels havolasini (linkini) yuboring, men uni sizga yuklab beraman! 🚀")

@bot.message_handler(func=lambda message: True)
def handle_instagram_link(message):
    url = message.text.strip()
    
    # Havolani tekshirish
    if "instagram.com" not in url:
        bot.reply_to(message, "Iltimos, faqat to'g'ri Instagram havolasini yuboring!")
        return

    msg = bot.reply_to(message, "Havola tekshirilmoqda va yuklanmoqda... ⏳")

    try:
        # Papkani tozalash
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
        else:
            for f in os.listdir("downloads"):
                try:
                    os.remove(os.path.join("downloads", f))
                except:
                    pass

        # REELS yoki POST (Rasm/Video) yuklash mantiqi
        if "/p/" in url or "/reels/" in url or "/reel/" in url:
            # Link ichidan shortcode (ID) ni qidirib topamiz
            match = re.search(r'(?:p|reel|reels)/([A-Za-z0-9_-]+)', url)
            if not match:
                bot.edit_message_text("Xatolik: Havola ichidan video ID-sini topib bo'lmadi.", message.chat.id, msg.message_id)
                return
                
            shortcode = match.group(1)
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target="downloads")
            
            # Yuklangan fayllarni foydalanuvchiga jo'natish
            files = os.listdir("downloads")
            video_sent = False
            photo_sent = False

            for file in files:
                file_path = os.path.join("downloads", file)
                if file.endswith('.mp4'):
                    with open(file_path, 'rb') as video:
                        bot.send_video(message.chat.id, video, caption="Mana siz so'ragan video! 🎬")
                        video_sent = True
                elif file.endswith('.jpg') and not video_sent:
                    # Agar video bo'lsa, rasmini qayta yubormaslik uchun tekshiramiz
                    with open(file_path, 'rb') as photo:
                        bot.send_photo(message.chat.id, photo, caption="Mana siz so'ragan rasm! 📸")
                        photo_sent = True
            
            # Kutish xabarini o'chirib tashlaymiz
            bot.delete_message(message.chat.id, msg.message_id)

        # STORIS yuklash mantiqi
        elif "/stories/" in url:
            # Storis yuklash uchun yuqoridagi login qismiga o'z profilingizni yozgan bo'lishingiz shart
            bot.edit_message_text("Storislarni yuklash funksiyasi faqat kod ichiga Instagram login/paroli kiritilganda ishlaydi.", message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("Xatolik: Faqat Post yoki Reels linkini yuboring.", message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"Yuklashda xatolik yuz berdi: {str(e)}\nEslatma: Profil yopiq (private) bo'lsa bot yuklay olmaydi.", message.chat.id, msg.message_id)

# Botni uzluksiz ishga tushirish
print("Instagram Downloader Bot tayyor...")
bot.infinity_polling()
