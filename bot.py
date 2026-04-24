import telebot
import random

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"

bot = telebot.TeleBot(TOKEN)

bot.delete_webhook()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Envoie une paire (ex: BTCUSDT) 📊")

@bot.message_handler(func=lambda message: True)
def reply(message):
    paire = message.text.upper()

    # liste des paires autorisées
    paires = ["BTCUSDT", "EURUSD", "USDJPY", "GBPUSD"]

    if paire in paires:
        signal = random.choice(["CALL 📈", "PUT 📉"])
        bot.send_message(message.chat.id, f"{paire} → {signal}")
    else:
        bot.send_message(message.chat.id, "Paire inconnue ❌")

print("Bot lancé...")
bot.infinity_polling()
