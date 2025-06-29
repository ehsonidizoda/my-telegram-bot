vvedicod_bot.py — Основной код Telegram-бота с функцией ввода кода и отправки видео.

import requests import time import sqlite3 from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

TOKEN = 'YOUR_BOT_TOKEN_HERE' ADMIN_ID = 7605086289

bot = Bot(TOKEN) db = sqlite3.connect('database.db', check_same_thread=False) cursor = db.cursor()

--- Создание таблиц ---

cursor.execute(''' CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY, lang TEXT, is_verified INTEGER DEFAULT 0 ) ''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS codes ( code TEXT PRIMARY KEY, file_id TEXT, description TEXT ) ''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS channels ( id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT ) ''')

db.commit()

--- Кнопки подписки ---

def get_sub_buttons(): cursor.execute("SELECT title, url FROM channels") rows = cursor.fetchall() buttons = [[InlineKeyboardButton(text=title, url=url)] for title, url in rows] return InlineKeyboardMarkup(buttons)

--- Стартовая команда ---

def start(update: Update, context): user_id = update.message.chat_id lang = 'ru' cursor.execute("INSERT OR IGNORE INTO users (id, lang) VALUES (?, ?)", (user_id, lang)) db.commit() text = "\u26a0\ufe0f Барои истифода бурдани бот ба канал\u04b3ои мо обуна шавед:" context.bot.send_voice(chat_id=user_id, voice=open('start.ogg', 'rb'), caption=text, reply_markup=get_sub_buttons())

--- Проверка подписки ---

def is_subscribed(bot, user_id): cursor.execute("SELECT url FROM channels") for (url,) in cursor.fetchall(): channel_username = url.split("t.me/")[-1] try: member = bot.get_chat_member(f"@{channel_username}", user_id) if member.status not in ["member", "administrator", "creator"]: return False except: return False return True

--- Обработка кода ---

def handle_code(update: Update, context): user_id = update.message.chat_id code = update.message.text.strip() cursor.execute("SELECT file_id, description FROM codes WHERE code = ?", (code,)) result = cursor.fetchone() if not result: update.message.reply_text("\u274c \u0411\u12b1 чунин \u0285\u0430\u049b\u0430 \u0275\u0438\u043b\u04d5 \u0451 \u0431\u04b1\u0440\u043d\u04ef\u043c\u0430 \u04bc\u0430\u0431\u04b3\u0443\u0434  \u043d\u0451\u0441\u0442 \u0451 \u0445\u04ef\u0440\u0438\u04b7 \u043a\u0430\u0440\u0434\u0430\u0430\u043d\u0434!") return file_id, description = result buttons = InlineKeyboardMarkup([ [ InlineKeyboardButton("\u041a\u0430\u043d\u0430\u043b \u043a\u043e\u0434\u043e\u0432", url="https://t.me/vkodkho"), InlineKeyboardButton("VIP", url="https://t.me/vipkodak"), ], [ InlineKeyboardButton("\u041f\u043e\u0434\u0435\u043b\u0438\u0442\u044c\u0441\u044f", switch_inline_query=description), InlineKeyboardButton("Instagram", url="https://instagram.com/your_page"), InlineKeyboardButton("\u0423\u0434\u0430\u043b\u0438\u0442\u044c", callback_data="delete") ] ]) update.message.reply_video(video=file_id, caption=description, reply_markup=buttons)

--- Удалить видео ---

def handle_callback(update: Update, context): query = update.callback_query if query.data == "delete": context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

--- Регистрация хендлеров ---

def main(): updater = Updater(TOKEN, use_context=True) dp = updater.dispatcher dp.add_handler(CommandHandler("start", start)) dp.add_handler(CallbackQueryHandler(handle_callback)) dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_code)) updater.start_polling() updater.idle()

if name == 'main': main()

