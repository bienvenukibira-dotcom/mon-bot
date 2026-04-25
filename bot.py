import telebot
import requests
import pandas as pd

print("VERSION PRO V1 🚀")

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"
API_KEY = "afca3d19871f415da626c918d9f565b0"

bot = telebot.TeleBot(TOKEN)

bot.delete_webhook()

# 📊 récupérer données
def get_data(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=50&apikey={API_KEY}"
        data = requests.get(url).json()

        if "values" not in data:
            print(data)
            return None

        closes = [float(c["close"]) for c in data["values"]]
        return pd.Series(closes[::-1])
    except Exception as e:
        print("ERREUR:", e)
        return None

# 📈 EMA
def ema(series, period):
    return series.ewm(span=period).mean()

# 🚀 démarrage
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot actif 🚀\nEnvoie EURUSD")

# 🧠 analyse
@bot.message_handler(func=lambda message: True)
def analyse(message):
    symbol = message.text.upper()

    data = get_data(symbol)

    if data is None:
        bot.send_message(message.chat.id, "Erreur données ❌")
        return

    ema20 = ema(data, 20).iloc[-1]
    ema50 = ema(data, 50).iloc[-1]

    if ema20 > ema50:
        bot.send_message(message.chat.id, f"{symbol} → CALL 🟢")
    else:
        bot.send_message(message.chat.id, f"{symbol} → PUT 🔴")

print("BOT LANCÉ ✅")
bot.infinity_polling()
