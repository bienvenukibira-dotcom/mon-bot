import telebot

# 🔴 MET TON TOKEN ICI DIRECTEMENT
TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"

bot = telebot.TeleBot(TOKEN)

# 🔥 évite erreur 409
bot.delete_webhook()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot actif ✅")

@bot.message_handler(func=lambda message: True)
def reply(message):
    bot.send_message(message.chat.id, "Je réponds 👍")

print("Bot lancé...")
bot.infinity_polling()
