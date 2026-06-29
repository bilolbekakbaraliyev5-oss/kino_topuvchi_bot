import telebot
import threading
from flask import Flask

# Tokeningizni kodga qo'shdik
TOKEN = '8794863028:AAFKU6QHjXiBR91W1sv3YhjpAXnoEal1uLc'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men ishlayapman.")

def run_server():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    # Serverni alohida oqimda ishga tushiramiz
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    # Botni ishga tushiramiz
    bot.infinity_polling()
