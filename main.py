vvedicod_bot.py — Основной код Telegram-бота с функцией ввода кода и отправки видео.

import requests import time import sqlite3 from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

TOKEN = 'YOUR_BOT_TOKEN_HERE' ADMIN_ID = 7605086289 bot = Bot(TOKEN) db = sqlite3.connect('database.db', check_same_thread=False) cursor = db.cursor()

--- Создание таблиц, если не существует ---

cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, lang TEXT, is_verified INTEGER DEFAULT 0)''') cursor.execute('''CREATE TABLE IF NOT EXISTS codes (code TEXT PRIMARY KEY, file_id TEXT, description TEXT)''') cursor.execute('''CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT)''') db.commit()

--- Кнопки подписки ---

def get_sub_buttons(): cursor.execute("SELECT title, url FROM channels") rows = cursor.fetchall() buttons = [[InlineKeyboardButton(row[0], url=row[1])] for row in rows] buttons.append([InlineKeyboardButton("✅ Я не робот", callback_data="verify")]) return InlineKeyboardMarkup(buttons)

--- /start ---

def start(update, context): user_id = update.message.from_user.id cursor.execute("INSERT OR IGNORE INTO users (id, lang) VALUES (?, 'ru')", (user_id,)) db.commit() bot.send_voice(chat_id=user_id, voice=open("welcome.ogg", "rb")) update.message.reply_text( "⚠️ Барои истифода бурдани бот ба каналҳои мо обуна шавед:", reply_markup=get_sub_buttons() )

--- Callback — проверка подписки ---

def callback_handler(update, context): query = update.callback_query user_id = query.from_user.id cursor.execute("UPDATE users SET is_verified=1 WHERE id=?", (user_id,)) db.commit() bot.send_message(user_id, "👋 Ꮯᴀᴧᴏʍ FORS , хуɯ ᴏʍᴀдᴇд бᴀ бᴏᴛи ʍᴏ.\n━━━━━━━━━━━━━\n✍🏻 Ꮲᴀʍɜи ɸиᴧʍᴩᴏ ɸиᴩиᴄᴛᴇд...")

--- Обработка кода ---

def handle_code(update, context): user_id = update.message.from_user.id text = update.message.text.strip() cursor.execute("SELECT file_id, description FROM codes WHERE code=?", (text,)) row = cursor.fetchone() if row: file_id, desc = row keyboard = InlineKeyboardMarkup([ [InlineKeyboardButton("Каналы кодов", url="https://t.me/example1")], [InlineKeyboardButton("VIP", url="https://t.me/example2")], [InlineKeyboardButton("Поделиться", switch_inline_query=desc)], [InlineKeyboardButton("Instagram", url="https://instagram.com/example")], [InlineKeyboardButton("🗑 Удалить", callback_data=f"del_{update.message.message_id}")], ]) bot.send_video(user_id, video=file_id, caption=desc, reply_markup=keyboard) else: update.message.reply_text("❌ Бᴀ чунин ᴩᴀʍɜ ɸиᴧʍ ё бᴀᴩнᴏʍᴀ ʍᴀʙҷуд  нᴇᴄᴛ ё хᴏᴩиҷ ᴋᴀᴩдᴀᴀнд!")

--- Удаление сообщения по кнопке ---

def del_handler(update, context): query = update.callback_query if query.data.startswith("del_"): try: bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id) except: pass

--- Основной запуск ---

def main(): updater = Updater(TOKEN, use_context=True) dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(callback_handler))
dp.add_handler(CallbackQueryHandler(del_handler, pattern="^del_"))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_code))

updater.start_polling()
updater.idle()

if name == 'main': main()

