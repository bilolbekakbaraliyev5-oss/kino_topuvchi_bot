import telebot
from telebot import types
from sqlitedict import SqliteDict
from flask import Flask
import threading

# Konfiguratsiyalar
TOKEN = '8794863028:AAEq_Jm0AhQml9A63n5csYsRQSXYramICcs'
ADMIN_ID = 8336384484
ADMIN_LINK = "https://t.me/Akbaral1yeevvv"
KANAL_CHLEN = "@kinolar_topuvchi"
KANAL_LINK = "https://t.me/kinolar_topuvchi"

# Bot va Baza
bot = telebot.TeleBot(TOKEN)
db = SqliteDict('./kino_baza.db', autocommit=True)

# Flask server qismi (Render uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_server():
    app.run(host='0.0.0.0', port=10000)

# Funksiyalar
def azo_bolganmi(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        status = bot.get_chat_member(chat_id=KANAL_CHLEN, user_id=user_id).status
        if status in ['creator', 'administrator', 'member']:
            return True
        return False
    except:
        return True

def majburiy_azolik_klaviaturasi():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(text="📢 KANALGA OBUNA BO'LISH", url=KANAL_LINK))
    markup.add(types.InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="tekshirish"))
    return markup

def asosiy_menyu_klaviaturasi():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("🔍 Kod orqali kinoni topish"), types.KeyboardButton("ℹ️ Biz haqimizda"))
    return markup

# Handlerlar
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if not azo_bolganmi(user_id):
        bot.send_message(message.chat.id, "👋 **Assalomu alaykum!**\n\nBotdan foydalanish uchun kanalga obuna bo'ling:", reply_markup=majburiy_azolik_klaviaturasi())
    else:
        bot.send_message(message.chat.id, f"👋 **Xush kelibsiz, {message.from_user.first_name}!**", reply_markup=asosiy_menyu_klaviaturasi())

@bot.callback_query_handler(func=lambda call: call.data == "tekshirish")
def check_callback(call):
    if azo_bolganmi(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!")
        bot.send_message(call.message.chat.id, "Marhamat, kod yuboring:", reply_markup=asosiy_menyu_klaviaturasi())
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo'lmadingiz!", show_alert=True)

@bot.message_handler(content_types=['text', 'video', 'document'])
def handle_all_messages(message):
    user_id = message.from_user.id
    
    # Admin kino qo'shishi
    if user_id == ADMIN_ID and (message.content_type in ['video', 'document']):
        if message.caption:
            kino_kodi = message.caption.strip()
            file_id = message.video.file_id if message.content_type == 'video' else message.document.file_id
            db[kino_kodi] = [file_id, 0, message.content_type]
            bot.reply_to(message, f"✅ Saqlandi! Kod: {kino_kodi}")
            return
        else:
            bot.reply_to(message, "❌ Videoga izoh (kod) qo'shing!")
            return

    # Foydalanuvchi qidiruvi
    if not azo_bolganmi(user_id):
        bot.send_message(message.chat.id, "⚠️ Kanalga obuna bo'ling!", reply_markup=majburiy_azolik_klaviaturasi())
        return

    if message.text == "🔍 Kod orqali kinoni topish":
        bot.send_message(message.chat.id, "✍️ Kino kodini yuboring:")
    elif message.text == "ℹ️ Biz haqimizda":
        bot.send_message(message.chat.id, "🤖 Kino Topuvchi Bot.\nSavollar uchun: " + ADMIN_LINK)
    elif message.text and message.text in db:
        data = db[message.text]
        data[1] += 1 # views
        db[message.text] = data
        if data[2] == 'video':
            bot.send_video(message.chat.id, data[0], caption=f"👁 Ko'rildi: {data[1]}")
        else:
            bot.send_document(message.chat.id, data[0], caption=f"👁 Ko'rildi: {data[1]}")
    else:
        bot.send_message(message.chat.id, "❌ Kino topilmadi.")

# Asosiy qism: Server va Bot birga ishlaydi
# Asosiy qism: Server va Bot birga ishlaydi
if __name__ == "__main__":
    # Serverni yurgizamiz
    threading.Thread(target=run_server, daemon=True).start()

    # Botni ishga tushirishdan oldin xabar chiqaramiz
    print("Bot polling boshlanyapti...")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"XATOLIK YUZ BERDI: {e}")
