import telebot
import random
from PIL import Image, ImageDraw

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDCAD", "EURJPY", "BTCUSDT"]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "BOT ACTIF 🚀\nEnvoie une paire")

@bot.message_handler(func=lambda message: True)
def analyse(message):
    pair = message.text.upper()

    if pair not in pairs:
        bot.send_message(message.chat.id, "Paire non supportée ❌")
        return

    signal = random.choice(["CALL", "PUT"])
    percent = random.randint(75, 95)

    img = Image.new('RGB', (500, 300), color='black')
    draw = ImageDraw.Draw(img)

    color = (0,255,0) if signal=="CALL" else (255,0,0)

    draw.text((180, 60), pair, fill="white")
    draw.text((200, 120), signal, fill=color)
    draw.text((200, 180), f"{percent}%", fill="white")

    img.save("signal.png")

    with open("signal.png", "rb") as photo:
        bot.send_photo(message.chat.id, photo)

bot.infinity_polling()
