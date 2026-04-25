import telebot
import requests
import pandas as pd

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"
API_KEY = "TA_CLE_API_ICI"

bot = telebot.TeleBot(TOKEN)
bot.delete_webhook()

def get_data(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=50&apikey={API_KEY}"
        data = requests.get(url).json()

        if "values" not in data:
            return None

        closes = [float(c["close"]) for c in data["values"]]
        return pd.Series(closes[::-1])
    except:
        return None

def ema(series, period):
    return series.ewm(span=period).mean()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot prêt 🚀\nEnvoie EURUSD ou GBPUSD")

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

print("Bot intelligent lancé...")
bot.infinity_polling()
