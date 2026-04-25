import telebot
import random
from PIL import Image, ImageDraw

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"
bot = telebot.TeleBot(TOKEN)

bot.delete_webhook()

# 🧠 analyse rapide (simulation intelligente)
def analyse():
    moves = [random.choice([1, -1]) for _ in range(20)]
    score_up = moves.count(1)
    score_down = moves.count(-1)

    if score_up > score_down:
        signal = "CALL"
        confidence = int((score_up / 20) * 100)
    else:
        signal = "PUT"
        confidence = int((score_down / 20) * 100)

    return signal, confidence

# 🎨 image propre
def create_image(signal, confidence, symbol):
    img = Image.new('RGB', (500, 300), color='black')
    draw = ImageDraw.Draw(img)

    color = (0,255,0) if signal == "CALL" else (255,0,0)

    draw.text((170, 60), symbol, fill="white")
    draw.text((180, 120), signal, fill=color)
    draw.text((180, 180), f"{confidence}%", fill="white")

    img.save("signal.png")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "BOT RAPIDE ACTIF ⚡\nEnvoie une paire (BTCUSDT...)")

@bot.message_handler(func=lambda message: True)
def handle(message):
    symbol = message.text.upper()

    signal, confidence = analyse()

    # 🎯 filtre
    if confidence < 60:
        bot.send_message(message.chat.id, f"{symbol} → PAS DE SIGNAL ❌ ({confidence}%)")
        return

    create_image(signal, confidence, symbol)

    with open("signal.png", "rb") as photo:
        bot.send_photo(message.chat.id, photo)

print("BOT 100% STABLE lancé...")
bot.infinity_polling()
