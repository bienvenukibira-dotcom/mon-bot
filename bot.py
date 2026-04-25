import telebot
import requests
import pandas as pd
from PIL import Image, ImageDraw

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

# 📊 données Binance
def get_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"
        data = requests.get(url).json()

        closes = [float(candle[4]) for candle in data]
        return pd.Series(closes)
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

# 📊 MACD
def macd(series):
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9).mean()
    return macd_line, signal

# 🎨 image
def create_image(signal, score, symbol):
    img = Image.new('RGB', (500, 300), color='black')
    draw = ImageDraw.Draw(img)

    color = (0,255,0) if signal == "CALL" else (255,0,0)

    draw.text((170, 60), symbol, fill="white")
    draw.text((180, 120), signal, fill=color)
    draw.text((180, 180), f"{score}%", fill="white")

    img.save("signal.png")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "BOT PRO CRYPTO 🚀\nEnvoie BTCUSDT")

@bot.message_handler(func=lambda message: True)
def analyse(message):
    symbol = message.text.upper()

    data = get_data(symbol)

    if data is None:
        bot.send_message(message.chat.id, "Erreur données ❌")
        return

    ema20 = ema(data, 20).iloc[-1]
    ema50 = ema(data, 50).iloc[-1]
    rsi_val = rsi(data).iloc[-1]

    macd_line, macd_signal = macd(data)
    macd_last = macd_line.iloc[-1]
    signal_last = macd_signal.iloc[-1]

    score = 0

    if ema20 > ema50:
        signal = "CALL"
        score += 40
    else:
        signal = "PUT"
        score += 40

    if signal == "CALL" and rsi_val < 60:
        score += 30
    elif signal == "PUT" and rsi_val > 40:
        score += 30

    if signal == "CALL" and macd_last > signal_last:
        score += 30
    elif signal == "PUT" and macd_last < signal_last:
        score += 30

    if score < 70:
        bot.send_message(message.chat.id, f"{symbol} → PAS DE SIGNAL ❌ ({score}%)")
        return

    create_image(signal, score, symbol)

    with open("signal.png", "rb") as photo:
        bot.send_photo(message.chat.id, photo)

bot.infinity_polling()
