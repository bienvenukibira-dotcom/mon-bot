import telebot
import requests
import pandas as pd

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"
bot = telebot.TeleBot(TOKEN)

bot.delete_webhook()

# 📊 récupérer données Binance
def get_data(symbol="BTCUSDT"):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"
    data = requests.get(url).json()
    closes = [float(c[4]) for c in data]
    return pd.Series(closes)

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

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Envoie une paire (BTCUSDT, EURUSD...) 📊")

@bot.message_handler(func=lambda message: True)
def analyse(message):
    symbol = message.text.upper()

    try:
        data = get_data(symbol)

        # indicateurs
        ema50 = ema(data, 50)
        ema200 = ema(data, 200)
        rsi_val = rsi(data).iloc[-1]
        macd_line, macd_signal = macd(data)

        # dernières valeurs
        ema50_last = ema50.iloc[-1]
        ema200_last = ema200.iloc[-1]
        macd_last = macd_line.iloc[-1]
        signal_last = macd_signal.iloc[-1]

        # 🎯 LOGIQUE INTELLIGENTE
        if ema50_last > ema200_last and rsi_val < 35 and macd_last > signal_last:
            bot.send_message(message.chat.id, f"{symbol} → CALL 📈 (tendance haussière confirmée)")
        
        elif ema50_last < ema200_last and rsi_val > 65 and macd_last < signal_last:
            bot.send_message(message.chat.id, f"{symbol} → PUT 📉 (tendance baissière confirmée)")
        
        else:
            bot.send_message(message.chat.id, f"{symbol} → PAS DE SIGNAL ❌ (conditions non réunies)")

    except:
        bot.send_message(message.chat.id, "Erreur paire ou marché ❌")

print("Bot PRO lancé...")
bot.infinity_polling()
