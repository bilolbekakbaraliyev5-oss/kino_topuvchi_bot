import os
from flask import Flask
from threading import Thread
import telebot
from telebot import types
from sqlitedict import SqliteDict

# Server sozlamalari
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=10000)

# Serverni fonda ishga tushirish
t = Thread(target=run)
t.start()

# Bot sozlamalari
TOKEN = '8794863028:AAFY4EaIfc3rURshxlWKDf9beaVJq3bfBtQ'
bot = telebot.TeleBot(TOKEN)
db = SqliteDict('./kino_baza.db', autocommit=True)

# Qolgan kodlaringizni (bot funksiyalarini) shu yerdan pastga yozing
# Masalan:
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Bot ishga tushdi.")

bot.polling(none_stop=True)
