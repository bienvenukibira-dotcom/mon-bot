import telebot
import requests
import pandas as pd
from PIL import Image, ImageDraw

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"
bot = telebot.TeleBot(TOKEN)

bot.delete_webhook()

# 🔧 BINANCE (source principale)
def get_binance(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"
        r = requests.get(url, timeout=5)
        data = r.json()

        if isinstance(data, dict):
            return None

        closes = [float(c[4]) for c in data]
        return pd.Series(closes)
    except:
        return None

# 🔧 FALLBACK (source alternative)
def get_alt(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        prices = []
        for _ in range(20):
            r = requests.get(url, timeout=3).json()
            prices.append(float(r["price"]))
        return pd.Series(prices)
    except:
        return None

# 📈 EMA
def ema(series, period):
    return series.ewm(span=period).mean()

# 📉 RSI
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 🎨 image
def create_image(signal, score, symbol):
    img = Image.new('RGB', (500, 300), color='black')
    draw = ImageDraw.Draw(img)

    color = (0,255,0) if signal == "CALL" else (255,0,0)

    draw.text((180, 60), symbol, fill="white")
    draw.text((180, 120), signal, fill=color)
    draw.text((180, 180), f"{score}%", fill="white")

    img.save("signal.png")

@bot.message_handler(func=lambda message: True)
def analyse(message):
    symbol = message.text.upper()

    data = get_binance(symbol)

    # 🔥 fallback si Binance ne marche pas
    if data is None:
        data = get_alt(symbol)

    if data is None:
        bot.send_message(message.chat.id, "Erreur données marché ❌")
        return

    # 🧠 logique rapide
    ema20 = ema(data, 20).iloc[-1]
    ema50 = ema(data, 50).iloc[-1]
    rsi_val = rsi(data).iloc[-1]

    score = 0

    if ema20 > ema50:
        signal = "CALL"
        score += 50
    else:
        signal = "PUT"
        score += 50

    if signal == "CALL" and rsi_val < 60:
        score += 30
    elif signal == "PUT" and rsi_val > 40:
        score += 30

    # 🎯 filtre
    if score < 60:
        bot.send_message(message.chat.id, f"{symbol} → PAS DE SIGNAL ❌ ({score}%)")
        return

    create_image(signal, score, symbol)

    with open("signal.png", "rb") as photo:
        bot.send_photo(message.chat.id, photo)

print("BOT STABLE lancé...")
bot.infinity_polling()
