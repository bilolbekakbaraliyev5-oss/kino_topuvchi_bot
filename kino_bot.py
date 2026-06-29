import telebot
from telebot import types
from sqlitedict import SqliteDict
from flask import Flask
import threading

# --- KONFIGURATSIYA ---
TOKEN = '8794863028:AAFY4EaIfc3rURshxlWKDf9beaVJq3bfBtQ'
ADMIN_ID = 8336384484
ADMIN_LINK = "https://t.me/Akbaral1yeevvv"
KANAL_CHLEN = "@kinolar_topuvchi"
KANAL_LINK = "https://t.me/kinolar_topuvchi"

# --- BAZA VA BOTNI ISHGA TUSHIRISH ---
bot = telebot.TeleBot(TOKEN)
db = SqliteDict('./kino_baza.db', autocommit=True)
app = Flask(__name__)

# --- SERVER QISMI (Render 24/7 ishlashi uchun) ---
@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_server():
    app.run(host='0.0.0.0', port=10000)

# --- FUNKSIYALAR ---
def azo_bolganmi(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        status = bot.get_chat_member(chat_id=KANAL_CHLEN, user_id=user_id).status
        return status in ['creator', 'administrator', 'member']
    except:
        return True

# --- HANDLERLAR ---
@bot.message_handler(commands=['start'])
def start_command(message):
    if not azo_bolganmi(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="📢 KANALGA OBUNA BO'LISH", url=KANAL_LINK))
        markup.add(types.InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="tekshirish"))
        bot.send_message(message.chat.id, "👋 Assalomu alaykum! Botdan foydalanish uchun kanalga obuna bo'ling:", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔍 Kod orqali kinoni topish", "ℹ️ Biz haqimizda")
        bot.send_message(message.chat.id, "👋 Xush kelibsiz!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "tekshirish")
def check_callback(call):
    if azo_bolganmi(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔍 Kod orqali kinoni topish", "ℹ️ Biz haqimizda")
        bot.send_message(call.message.chat.id, "Marhamat, kino kodini yuboring:", reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo'lmadingiz!", show_alert=True)

@bot.message_handler(content_types=['text', 'video', 'document'])
def handle_messages(message):
    user_id = message.from_user.id

    # Admin kino qo'shish qismi
    if user_id == ADMIN_ID and (message.content_type in ['video', 'document']):
        if message.caption:
            db[message.caption.strip()] = [message.video.file_id if message.video else message.document.file_id, 0, message.content_type]
            bot.reply_to(message, "✅ Kino bazaga saqlandi!")
            return
        else:
            bot.reply_to(message, "❌ Iltimos, videoga kodni izoh qilib yozing.")
            return

    # Foydalanuvchi qismi
    if not azo_bolganmi(user_id):
        bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun kanalga obuna bo'ling.")
        return

    if message.text == "🔍 Kod orqali kinoni topish":
        bot.send_message(message.chat.id, "✍️ Kino kodini yuboring:")
    elif message.text == "ℹ️ Biz haqimizda":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="👨‍💻 Admin bilan aloqa", url=ADMIN_LINK))
        bot.send_message(message.chat.id, "🤖 Kino Topuvchi Bot.\nBiz sizga eng sifatli kinolarni topishda yordam beramiz!", reply_markup=markup)
    elif message.text in db:
        data = db[message.text]
        data[1] += 1
        db[message.text] = data
        if data[2] == 'video':
            bot.send_video(message.chat.id, data[0], caption=f"👁 Ko'rildi: {data[1]}")
        else:
            bot.send_document(message.chat.id, data[0], caption=f"👁 Ko'rildi: {data[1]}")
    else:
        bot.send_message(message.chat.id, "❌ Kino topilmadi.")

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    print("Bot muvaffaqiyatli ishga tushdi!")
    bot.infinity_polling()
