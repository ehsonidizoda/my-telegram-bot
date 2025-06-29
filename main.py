import sqlite3
import logging
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# Конфигурация
TOKEN = 'YOUR_BOT_TOKEN_HERE'
ADMIN_ID = 7605086289
DB_NAME = 'database.db'
WELCOME_VOICE = 'welcome.ogg'

# Инициализация бота и базы данных
bot = Bot(TOKEN)
db = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = db.cursor()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Создание таблиц ---
def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            lang TEXT DEFAULT 'ru',
            is_verified INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY, 
            file_id TEXT,
            description TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT, 
            url TEXT UNIQUE
        )
    ''')
    db.commit()

# --- Кнопки подписки ---
def get_sub_buttons():
    cursor.execute("SELECT title, url FROM channels")
    channels = cursor.fetchall()
    
    buttons = []
    for title, url in channels:
        buttons.append([InlineKeyboardButton(title, url=url)])
    
    buttons.append([InlineKeyboardButton("✅ Я не робот", callback_data="verify")])
    return InlineKeyboardMarkup(buttons)

# --- /start команда ---
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    # Добавляем пользователя в БД
    cursor.execute(
        "INSERT OR IGNORE INTO users (id) VALUES (?)",
        (user_id,)
    )
    db.commit()
    
    try:
        # Отправляем голосовое приветствие
        with open(WELCOME_VOICE, 'rb') as voice_file:
            update.message.reply_voice(voice=voice_file)
    except FileNotFoundError:
        logger.error(f"Voice file {WELCOME_VOICE} not found!")
    
    # Отправляем сообщение с кнопками
    update.message.reply_text(
        "⚠️ Барои истифода бурдани бот ба каналҳои мо обуна шавед:",
        reply_markup=get_sub_buttons()
    )

# --- Проверка подписки ---
def check_subscription(user_id: int) -> bool:
    # Здесь должна быть реализована проверка подписки на каналы
    # Временно возвращаем True для тестирования
    return True

# --- Обработчик кнопок ---
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    # Обработка верификации
    if data == "verify":
        if check_subscription(user_id):
            cursor.execute(
                "UPDATE users SET is_verified=1 WHERE id=?",
                (user_id,)
            )
            db.commit()
            query.answer()
            query.edit_message_text("👋 Хуш омадед ба боти мо!\n━━━━━━━━━━━━━\n✍🏻 Лутфан рамзро фиристед...")
        else:
            query.answer("❌ Шумо ҳамаи каналҳоро обуна нашудаед!", show_alert=True)
    
    # Обработка кнопки удаления
    elif data.startswith("del_"):
        try:
            message_id = int(data.split("_")[1])
            context.bot.delete_message(
                chat_id=query.message.chat_id,
                message_id=message_id
            )
            query.answer()
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            query.answer("❌ Хато дар ҳазф кардан!")

# --- Обработка кодов ---
def handle_code(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    code = update.message.text.strip().upper()
    
    # Проверка верификации пользователя
    cursor.execute("SELECT is_verified FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    
    if not user or not user[0]:
        update.message.reply_text(
            "❌ Илтимос аввал обуна шавед!",
            reply_markup=get_sub_buttons()
        )
        return
    
    # Поиск кода в базе
    cursor.execute(
        "SELECT file_id, description FROM codes WHERE code=?",
        (code,)
    )
    result = cursor.fetchone()
    
    if result:
        file_id, description = result
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Каналы кодов", url="https://t.me/example1"),
                InlineKeyboardButton("VIP", url="https://t.me/example2")
            ],
            [InlineKeyboardButton("Поделиться", switch_inline_query=code)],
            [InlineKeyboardButton("Instagram", url="https://instagram.com/example")],
            [InlineKeyboardButton("🗑 Удалить", callback_data=f"del_{update.message.message_id}")]
        ])
        
        update.message.reply_video(
            video=file_id,
            caption=description,
            reply_markup=keyboard
        )
    else:
        update.message.reply_text("❌ Рамз ёфт нашуд!")

# --- Основная функция ---
def main():
    init_db()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Регистрация обработчиков
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_code))

    # Запуск бота
    updater.start_polling()
    logger.info("Bot started polling...")
    updater.idle()

if __name__ == '__main__':
    main()