import telebot

BOT_TOKEN = "7205626251:AAFpB3EtXv-mNyKWXP4IBa7ZCqNqzn2tL0E"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, "Привет! Я бот, и я работаю на Railway!")

print("Бот запущен...")
bot.polling()
