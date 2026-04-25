import telebot

print("VERSION TEST UNIQUE 12345 🚀")

TOKEN = "8759628647:AAH6XfSmHCHQgt-b4ODJAmgQHE40HGZaCcw"
bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()

@bot.message_handler(func=lambda message: True)
def reply(message):
    bot.send_message(message.chat.id, "VERSION 12345 OK")

bot.infinity_polling()
