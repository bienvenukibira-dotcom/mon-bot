import telebot
import os
import random
from PIL import Image, ImageDraw

# 🔑 récupérer le token depuis Render
TOKEN = os.getenv("8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw")

if not TOKEN:
    print("TOKEN manquant ❌")
    exit()

bot = telebot.TeleBot(TOKEN)

# 🔥 corrige erreur 409
bot.delete_webhook()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot actif ✅")

@bot.message_handler(func=lambda message: True)
def reply(message):
    signal = random.choice(["CALL", "PUT"])

    img = Image.new('RGB', (400, 300), color='black')
    draw = ImageDraw.Draw(img)

    color = (0,255,0) if signal=="CALL" else (255,0,0)
    draw.text((150,130), signal, fill=color)

    img.save("signal.png")

    with open("signal.png", "rb") as photo:
        bot.send_photo(message.chat.id, photo)

print("Bot lancé...")
bot.infinity_polling()
