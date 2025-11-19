import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import mysql.connector
import logging
import sys


bot  = telebot.TeleBot('BOT_TOKEN', parse_mode= 'html')


logging.basicConfig(level=logging.WARNING, handlers=[])
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(' - %(name)s - %(levelname)s - %(message)s')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
stdout_handler.setFormatter(formatter)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.WARNING)
stderr_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)

level = {}

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id in [5075300738] :
        kb = InlineKeyboardMarkup(row_width=1)
        btn_settings = InlineKeyboardButton("🛠️ Настройки", callback_data="btn_settings")
        kb.add(btn_settings)
        data = get()
        status = data['status']
        mode = data['mode']
        gpt = data['GPT']
        chats = data['chats']
        if chats: chats= chats.replace(' ','').replace(',',', ')
        autoresponder = data['autoresponder']
        if status == 'work':
            btn_stop = InlineKeyboardButton("⏹️ Остановить", callback_data="btn_stop")
            kb.add(btn_stop)
        else:
            btn_start = InlineKeyboardButton("🚀 Запустить", callback_data="btn_start")
            kb.add(btn_start)
        bot.send_message(message.chat.id, f'<b><i>🏠 Меню автоответчика</i></b>\n<blockquote><b>📍 Статус:</b> {status}\n<b>📑 Текущий режим:</b> {mode}\n<b>💬 Чаты:</b> {chats}\n<b>🧠 GPT промпт:</b> {gpt}\n<b>📙 Текст автоответчика:</b> {autoresponder}</blockquote>', reply_markup=kb)

    else:
        bot.send_message(message.chat.id, '⛔ У вас нет доступа к настройке автоответчика')








@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    message = callback.message
    if callback.data == "btn_stop":
        put(5075300738, 'status', 'stop')
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        start(message)
    elif callback.data == "btn_start":
        put(5075300738, 'status', 'work')
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        start(message)
    elif callback.data == "btn_settings":
        kb = InlineKeyboardMarkup(row_width=1)
        btn_chat = InlineKeyboardButton("💬 Выбор чатов", callback_data="btn_chat")
        btn_choice_mode = InlineKeyboardButton("📑 Выбор режима", callback_data="btn_choice_mode")
        btn_settings_mode = InlineKeyboardButton("🔧Настроить режимы", callback_data="btn_settings_mode")
        btn_back = InlineKeyboardButton("🏠 В меню", callback_data="btn_back")
        kb.add(btn_chat,btn_choice_mode,btn_settings_mode,btn_back)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text='🛠️ Настройки', reply_markup = kb)
    elif callback.data == "btn_chat":
        kb = InlineKeyboardMarkup(row_width=1)
        btn_all = InlineKeyboardButton("🔑 Выбрать все чаты", callback_data="btn_all")
        level[message.chat.id] = 'get_chat'
        btn_back = InlineKeyboardButton("🏠 В меню", callback_data="btn_back")
        kb.add(btn_all,btn_back)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text='💬 Введите чаты через запятую', reply_markup=kb)
    elif callback.data == 'btn_back':
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        start(message)
    elif callback.data == 'btn_choice_mode':
        kb = InlineKeyboardMarkup(row_width=1)
        btn_autoresponder = InlineKeyboardButton("📲 Автоответчик", callback_data="btn_autoresponder")
        btn_GPT = InlineKeyboardButton("🧠 GPT", callback_data="btn_GPT")
        btn_back = InlineKeyboardButton("🏠 В меню", callback_data="btn_back")
        kb.add(btn_autoresponder,btn_GPT, btn_back)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text='📑 Выбери режим', reply_markup=kb)
    elif callback.data == 'btn_settings_mode':
        kb = InlineKeyboardMarkup(row_width=1)
        btn_autoresponder = InlineKeyboardButton("📲 Автоответчик", callback_data="btn_settings_autoresponder")
        btn_GPT = InlineKeyboardButton("🧠 GPT", callback_data="btn_settings_GPT")
        btn_back = InlineKeyboardButton("🏠 В меню", callback_data="btn_back")
        kb.add(btn_autoresponder, btn_GPT, btn_back)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text= '📑 Выбери режим', reply_markup=kb)
    elif callback.data == 'btn_autoresponder':
        put('5075300738', 'mode', 'autoresponder')
        bot.edit_message_text(chat_id=message.chat.id,message_id=message.id, text = '✅ Установлен режим автоответчика')
        start(message)
    elif callback.data == 'btn_GPT':
        put('5075300738', 'mode', 'GPT')
        bot.edit_message_text(chat_id=message.chat.id,message_id=message.id, text = '✅ Установлен режим GPT')
        start(message)
    elif callback.data == 'btn_all':
        put('5075300738', 'chats' , 'all')
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text='✅ Установлены все личные чаты')
        level[message.chat.id] = 'menu'
        start(message)
    elif callback.data == 'btn_settings_autoresponder':
        kb = InlineKeyboardMarkup(row_width=1)
        btn_back = InlineKeyboardButton("🏠 В меню", callback_data="btn_back")
        kb.add(btn_back)
        level[message.chat.id] = 'get_autoresponder_text'
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text='🖊️ Введи текст автоответчика', reply_markup=kb)
    elif callback.data == 'btn_settings_GPT':
        kb = InlineKeyboardMarkup(row_width=1)
        btn_skip = InlineKeyboardButton("Пропустить", callback_data="btn_skip")
        btn_back = InlineKeyboardButton("🏠 В меню", callback_data="btn_back")
        kb.add(btn_skip, btn_back)
        level[message.chat.id] = 'get_GPT_text'
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text='🖊️ Введи промпт для gpt', reply_markup=kb)
    elif callback.data == 'btn_skip':
        put('5075300738', 'GPT', '')
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text='🧠 GPT без системного промпта')
        level[message.chat.id] = 'menu'
        start(message)



@bot.message_handler(content_types = ['text'])
def text(message):
    if level[message.chat.id] == 'get_GPT_text':
        put('5075300738', 'GPT', message.text)
        bot.send_message(chat_id=message.chat.id, text=f'✅ Установлен промпт для GPT: <blockquote>{message.text}</blockquote>')
        level[message.chat.id] = 'menu'
        start(message)
    elif level[message.chat.id] == 'get_chat':
        put('5075300738', 'chats', message.text)
        bot.send_message(chat_id=message.chat.id,  text=f'✅ Установлены чаты: <blockquote>{message.text}</blockquote>')
        level[message.chat.id] = 'menu'
        start(message)
    elif level[message.chat.id] == 'get_autoresponder_text':
        put('5075300738', 'autoresponder', message.text)
        bot.send_message(chat_id=message.chat.id, text=f'✅ Установлен текст для автоответчика: <blockquote>{message.text}</blockquote>')
        level[message.chat.id] = 'menu'
        start(message)




def put(user_id, k, level):
    try:
        logger.info(f'Запущена запись ')
        mydb = bd_connect()
        cursor = mydb.cursor(dictionary=True)
        sql = f'INSERT INTO autosend (id, {k}) VALUES (%s, %s) ON DUPLICATE KEY UPDATE {k} = VALUES({k});'
        cursor.execute(sql, (user_id, level))
        mydb.commit()
        cursor.close()
        mydb.close()
    except Exception as e:
        logger.exception(f'Ошибка: {e}')
    else:
        logger.info(f'{k}: {level} записан для : {user_id}')


def get():
    try:
        logger.info('Запущен get')
        mydb = bd_connect()
        cursor = mydb.cursor(dictionary=True)
        sql = f"SELECT * FROM autosend"
        cursor.execute(sql, )
        rows = cursor.fetchall()
        mydb.commit()
        cursor.close()
        mydb.close()
        logger.info(rows)
    except Exception as e:
        logger.exception(f'Ошибка: {e}')
    else:
        logger.info(f'Получена информация ')
        return rows[0] if rows else None



def bd_connect():
    k = 0
    while k <= 5:
        try:
            mydb = mysql.connector.connect(
                host='HOST',
                user='USER',
                port=3306,
                password='PASSWORD',
                database='DATEBASE'
            )
        except mysql.connector.Error as err:
            logger.exception(f"Ошибка подключения к базе данных: {err}")
            k += 1
        else:
            logger.info('Успешное подключение к БД')
            return mydb
    return None


if __name__ == '__main__':
    bot.polling(non_stop=True)