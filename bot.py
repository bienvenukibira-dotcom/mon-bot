import telebot
import random
from PIL import Image, ImageDraw

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDCAD", "EURJPY"]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot prêt 🚀\nEnvoie une paire (ex: EURUSD)")

@bot.message_handler(func=lambda message: True)
def analyse(message):
    pair = message.text.upper()

    if pair not in pairs:
        bot.send_message(message.chat.id, "Paire non supportée ❌")
        return

    signal = random.choice(["CALL", "PUT"])
    percent = random.randint(75, 95)

    img = Image.new('RGB', (400, 300), color='black')
    draw = ImageDraw.Draw(img)

    color = (0,255,0) if signal=="CALL" else (255,0,0)
    text = f"{pair}\n{signal}\n{percent}%"

    draw.text((120,120), text, fill=color)

    img.save("signal.png")

    with open("signal.png", "rb") as photo:
        bot.send_photo(message.chat.id, photo)

bot.infinity_polling()
