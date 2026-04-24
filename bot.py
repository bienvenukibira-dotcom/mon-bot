import telebot
import requests
from PIL import Image, ImageDraw

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"
bot = telebot.TeleBot(TOKEN)

bot.delete_webhook()

# 📊 récupérer bougies 1 minute
def get_candles(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=20"
        data = requests.get(url, timeout=5).json()
        closes = [float(c[4]) for c in data]
        return closes
    except:
        return None

# 🧠 analyse M1
def analyse(symbol):
    closes = get_candles(symbol)
    if not closes:
        return None, 0

    up = 0
    down = 0

    for i in range(len(closes)-1):
        if closes[i+1] > closes[i]:
            up += 1
        else:
            down += 1

    total = up + down

    if up > down:
        signal = "CALL"
        confidence = int((up / total) * 100)
    else:
        signal = "PUT"
        confidence = int((down / total) * 100)

    return signal, confidence

# 🎨 image
def create_image(signal, confidence, symbol):
    img = Image.new('RGB', (500, 300), color='black')
    draw = ImageDraw.Draw(img)

    color = (0,255,0) if signal == "CALL" else (255,0,0)

    draw.text((180, 60), symbol, fill="white")
    draw.text((180, 120), signal, fill=color)
    draw.text((180, 180), f"{confidence}%", fill="white")

    img.save("signal.png")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Envoie une paire (BTCUSDT, EURUSD...) ⏱ M1")

@bot.message_handler(func=lambda message: True)
def handle(message):
    symbol = message.text.upper()

    signal, confidence = analyse(symbol)

    if signal is None:
        bot.send_message(message.chat.id, "Erreur paire ❌")
        return

    create_image(signal, confidence, symbol)

    with open("signal.png", "rb") as photo:
        bot.send_photo(message.chat.id, photo)

print("Bot M1 lancé...")
bot.infinity_polling()
