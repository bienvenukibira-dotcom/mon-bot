import telebot
import os

TOKEN = os.getenv("8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw")

if not TOKEN:
    print("TOKEN manquant ❌")
    exit()

bot = telebot.TeleBot(TOKEN)

bot.delete_webhook()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot actif ✅")

@bot.message_handler(func=lambda message: True)
def reply(message):
    bot.send_message(message.chat.id, "Je réponds 👍")

print("Bot lancé...")
bot.infinity_polling()
