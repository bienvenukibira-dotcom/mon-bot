import telebot
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import BollingerBands
from PIL import Image, ImageDraw

bot = telebot.TeleBot("8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw")

# 📡 récupérer données
def get_data(symbol, interval):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    df[4] = df[4].astype(float)
    df[2] = df[2].astype(float)
    df[3] = df[3].astype(float)
    return df

# 🧠 analyse timeframe
def analyze_tf(df):
    close = df[4]
    high = df[2]
    low = df[3]

    rsi = RSIIndicator(close).rsi().iloc[-1]
    ema = EMAIndicator(close, window=20).ema_indicator().iloc[-1]

    macd = MACD(close)
    macd_val = macd.macd().iloc[-1]
    macd_signal = macd.macd_signal().iloc[-1]

    bb = BollingerBands(close)
    upper = bb.bollinger_hband().iloc[-1]
    lower = bb.bollinger_lband().iloc[-1]

    adx = ADXIndicator(high, low, close).adx().iloc[-1]

    price = close.iloc[-1]

    score = 0

    if rsi < 35:
        score += 1
    elif rsi > 65:
        score -= 1

    if price > ema:
        score += 1
    else:
        score -= 1

    if macd_val > macd_signal:
        score += 1
    else:
        score -= 1

    if price < lower:
        score += 1
    elif price > upper:
        score -= 1

    if adx > 25:
        score *= 1.5
    else:
        score *= 0.5

    return score, rsi, adx

# 🔥 analyse globale
def analyze(symbol):
    tfs = ["1m", "5m", "15m"]
    scores = []
    last_rsi = 0
    last_adx = 0

    for tf in tfs:
        df = get_data(symbol, tf)
        score, rsi, adx = analyze_tf(df)
        scores.append(score)
        last_rsi = rsi
        last_adx = adx

    total_score = sum(scores)

    # 🎯 confiance améliorée
    confidence = abs(total_score) * 15

    if all(s > 0 for s in scores) or all(s < 0 for s in scores):
        confidence += 20

    if last_adx > 25:
        confidence += 15

    confidence = min(confidence, 100)

    # 🚀 décision
    if total_score >= 0:
        signal = "CALL"
    else:
        signal = "PUT"

    return signal, confidence, last_rsi, last_adx

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot SNIPER 🎯\nEx: BTCUSDT ou EURUSD")

@bot.message_handler(func=lambda message: True)
def reply(message):
    text = message.text.upper()

    # 🔁 conversion forex
    if text == "EURUSD":
        symbol = "EURUSDT"
    elif text == "GBPUSD":
        symbol = "GBPUSDT"
    else:
        symbol = text

    try:
        signal, confidence, rsi, adx = analyze(symbol)

        img = Image.new('RGB', (450, 340), color='black')
        draw = ImageDraw.Draw(img)

        if signal == "CALL":
            color = (0,255,0)
            arrow = "↑"
        else:
            color = (255,0,0)
            arrow = "↓"

        draw.text((120,60), symbol, fill=(255,255,255))
        draw.text((120,110), f"{signal} {arrow}", fill=color)
        draw.text((120,170), f"Conf: {int(confidence)}%", fill=(255,255,0))
        draw.text((120,220), f"RSI: {round(rsi,2)}", fill=(255,255,255))
        draw.text((120,270), f"ADX: {round(adx,2)}", fill=(255,255,255))

        img.save("signal.png")

        with open("signal.png", "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=f"{symbol}\nSignal: {signal}\nConfiance: {int(confidence)}%"
            )

    except Exception as e:
        print("ERREUR:", e)
        bot.send_message(message.chat.id, "Erreur ❌")

bot.infinity_polling()
