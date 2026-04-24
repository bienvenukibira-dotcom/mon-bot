import telebot
import requests
import pandas as pd
from PIL import Image, ImageDraw

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"
bot = telebot.TeleBot(TOKEN)

bot.delete_webhook()

# 🔧 récupération données robuste
def get_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=120"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        if isinstance(data, dict) and "code" in data:
            return None

        df = pd.DataFrame(data, columns=[
            "time","open","high","low","close","volume",
            "ct","qv","nt","tb","tq","ignore"
        ])

        df["close"] = df["close"].astype(float)
        df["open"] = df["open"].astype(float)

        return df

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

# 📉 engulfing simple
def engulfing(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if prev["close"] < prev["open"] and last["close"] > last["open"] and last["close"] > prev["open"]:
        return "CALL"

    if prev["close"] > prev["open"] and last["close"] < last["open"] and last["close"] < prev["open"]:
        return "PUT"

    return None

# 🎨 image
def create_image(signal, score, symbol):
    img = Image.new('RGB', (500, 300), color='black')
    draw = ImageDraw.Draw(img)

    color = (0,255,0) if signal == "CALL" else (255,0,0)

    draw.text((180, 60), symbol, fill="white")
    draw.text((180, 120), signal, fill=color)
    draw.text((180, 180), f"{score}%", fill="white")

    img.save("signal.png")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "ULTRA SNIPER prêt 🔥\nEnvoie BTCUSDT ou autre paire")

@bot.message_handler(func=lambda message: True)
def analyse(message):
    symbol = message.text.upper()

    df = get_data(symbol)

    if df is None:
        bot.send_message(message.chat.id, "Erreur paire ❌")
        return

    close = df["close"]

    ema50 = ema(close, 50).iloc[-1]
    ema200 = ema(close, 200).iloc[-1]
    rsi_val = rsi(close).iloc[-1]

    macd_line, macd_signal = macd(close)
    macd_last = macd_line.iloc[-1]
    signal_last = macd_signal.iloc[-1]

    engulf = engulfing(df)

    score = 0

    if ema50 > ema200:
        trend = "UP"
        score += 20
    else:
        trend = "DOWN"
        score += 20

    if trend == "UP" and 30 < rsi_val < 50:
        score += 20
    elif trend == "DOWN" and 50 < rsi_val < 70:
        score += 20

    if trend == "UP" and macd_last > signal_last:
        score += 20
    elif trend == "DOWN" and macd_last < signal_last:
        score += 20

    if engulf == "CALL" and trend == "UP":
        score += 30
    elif engulf == "PUT" and trend == "DOWN":
        score += 30

    if score >= 75:
        signal = "CALL" if trend == "UP" else "PUT"
        create_image(signal, score, symbol)

        with open("signal.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, f"{symbol} → PAS DE SIGNAL ❌ ({score}%)")

print("ULTRA SNIPER BOT lancé...")
bot.infinity_polling()
