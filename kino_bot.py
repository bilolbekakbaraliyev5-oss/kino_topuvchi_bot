from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=10000)

# Buni kodning eng oxiriga yoki asosiy qismiga qo'shing:
t = Thread(target=run)
t.start()
import os
from flask import Flask
from threading import Thread
import telebot
from telebot import types
from sqlitedict import SqliteDict

TOKEN = '8794863028:AAFY4EaIfc3rURshxlWKDf9beaVJq3bfBtQ'
ADMIN_ID = 8336384484
ADMIN_LINK = "https://t.me/Akbaral1yeevvv"
KANAL_CHLEN = "@kinolar_topuvchi"
KANAL_LINK = "https://t.me/kinolar_topuvchi"

bot = telebot.TeleBot(TOKEN)
db = SqliteDict('./kino_baza.db', autocommit=True)

def azo_bolganmi(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        status = bot.get_chat_member(chat_id=KANAL_CHLEN, user_id=user_id).status
        if status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Xatolik: {e}")
        return True

def majburiy_azolik_klaviaturasi():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(text="📢 KANALGA OBUNA BO'LISH", url=KANAL_LINK))
    markup.add(types.InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="tekshirish"))
    return markup

def asosiy_menyu_klaviaturasi():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    t1 = types.KeyboardButton("🔍 Kod orqali kinoni topish")
    t2 = types.KeyboardButton("ℹ️ Biz haqimizda")
    markup.add(t1, t2)
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if not azo_bolganmi(user_id):
        bot.send_message(
            message.chat.id, 
            "👋 **Assalomu alaykum!**\n\nBotdan to'liq foydalanish uchun quyidagi kanalimizga obuna bo'ling va **✅ Obuna bo'ldim** tugmasini bosing! 🚀", 
            reply_markup=majburiy_azolik_klaviaturasi()
        )
    else:
        bot.send_message(
            message.chat.id, 
            f"👋 **Xush kelibsiz, {message.from_user.first_name}!**\n\nKino kodini yuboring yoki quyidagi menyudan foydalaning: 👇", 
            reply_markup=asosiy_menyu_klaviaturasi()
        )

@bot.message_handler(commands=['panel'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            f"📊 **Admin Panel**\n\n🎬 Bazadagi jami kinolar: {len(db)} ta\n\n🆕 **Kino qo'shish:** Videoni yuklab, ostiga faqat kodini yozing."
        )
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat admin uchun!")

@bot.callback_query_handler(func=lambda call: call.data == "tekshirish")
def check_callback(call):
    user_id = call.from_user.id
    if azo_bolganmi(user_id):
        bot.answer_callback_query(call.id, "🎉 Rahmat! Obuna tasdiqlandi.")
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(
            call.message.chat.id, 
            "✅ **Obuna tasdiqlandi!** 🎉\n\nMarhamat, kino kodini yuborishingiz mumkin:", 
            reply_markup=asosiy_menyu_klaviaturasi()
        )
    else:
        bot.answer_callback_query(call.id, "❌ Hali ko'rsatilgan kanalga obuna bo'lmadingiz!", show_alert=True)

@bot.message_handler(content_types=['text', 'video', 'document'])
def handle_all_messages(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID and (message.content_type == 'video' or message.content_type == 'document'):
        if message.caption:
            kino_kodi = message.caption.strip()
            fayl_turi = "video" if message.content_type == 'video' else "file"
            file_id = message.video.file_id if message.content_type == 'video' else message.document.file_id
            db[kino_kodi] = [file_id, 0, fayl_turi]
            bot.reply_to(message, f"✅ **Kino bazaga muvaffaqiyatli saqlandi!**\n🔑 **Kino kodi:** {kino_kodi}")
        else:
            bot.reply_to(message, "❌ **Xatolik:** Videoni ostiga kino kodini yozib yuboring!")
        return

    if not azo_bolganmi(user_id):
        bot.send_message(
            message.chat.id, 
            "⚠️ **Botdan foydalanish uchun avval kanalga obuna bo'lishingiz shart:**", 
            reply_markup=majburiy_azolik_klaviaturasi()
        )
        return

    if message.content_type == 'text':
        tekst = message.text.strip()
        if tekst == "🔍 Kod orqali kinoni topish":
            bot.send_message(message.chat.id, "✍️ Marhamat, kino kodini yuboring (Masalan: 101):")
        elif tekst == "ℹ️ Biz haqimizda":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="👨‍💻 Admin bilan aloqa", url=ADMIN_LINK))
            
            matn = (
                "🤖 **Kino Topuvchi Bot**\n\n"
                "Bu bot orqali siz kanaldagi kinolarni maxsus kodlar yordamida tezkor va qulay yuklab olishingiz mumkin! 🎬\n\n"
                "💡 Takliflar yoki savollar bo'lsa, adminga murojaat qiling:"
            )
            bot.send_message(message.chat.id, matn, reply_markup=markup, parse_mode="Markdown")
        else:
            kino_kodi = tekst
            if kino_kodi in db:
                kino_data = db[kino_kodi]
                file_id = kino_data[0]
                views = kino_data[1] + 1
                fayl_turi = kino_data[2] if len(kino_data) > 2 else "video"
                db[kino_kodi] = [file_id, views, fayl_turi]
                
                bot.send_message(message.chat.id, "🎬 **Kino topildi! Yuklanmoqda, iltimos kuting...** 🚀")
                matn = f"🎬 **Kino kodi:** {kino_kodi}\n👁 **Ko'rdi:** {views} kishi"
                
                if fayl_turi == "video":
                    bot.send_video(message.chat.id, file_id, caption=matn, parse_mode="Markdown")
                else:
                    bot.send_document(message.chat.id, file_id, caption=matn, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ **Afsuski, bu kod bilan kino topilmadi.**\n\nKodni to'g'ri yozganingizni qayta tekshirib ko'ring.")

print("Kino bot yangilangan holatda ishga tushdi...")
bot.infinity_polling()
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

t = Thread(target=run)
t.start()
