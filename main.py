from openai import OpenAI
from telethon import TelegramClient, events
import asyncio
import traceback
import mysql.connector
import logging
import sys

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

messages = {}

API_ID = 'API_ID'
API_HASH = 'API_HASH'
PHONE_NUMBER = 'PHONE_NUMBER'

client = TelegramClient(f'session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def reply_to_message(event):
    try:
        data = get()
        status = data['status']
        chats = data['chats']
        if status == 'work' and ((chats == 'all' and str(event.chat_id)[0] != '-') or str(event.chat_id) in chats.replace(' ','').split(',')):
            if chats == 'all':
                user = await event.get_sender()
                if user.bot:
                    return
                if event.sender and event.sender.bot:
                    return
            mode = data['mode']
            if mode == 'GPT':
                SYSTEM_PROMPT = data['GPT']
                ai_client = OpenAI(
                    api_key='API_KEY',
                    base_url='URL'
                )

                if (event.chat_id not in messages) or ({'role': 'system', 'content': SYSTEM_PROMPT} not in messages[event.chat_id]):
                    messages[event.chat_id] = [{'role': 'system', 'content': SYSTEM_PROMPT}] 
                messages[event.chat_id].append(
                    {
                        'role': 'user',
                        'content': event.text
                    }
                )
                response = ai_client.chat.completions.create(
                    model='MODEL',
                    messages=messages[event.chat_id],
                    temperature=0.1
                )
                text = response.choices[0].message.content
                await event.reply(text)
                messages[event.chat_id].append(
                    {
                        'role': 'assistant',
                        'content': text
                    }
                )
            else:
                autoresponder = data['autoresponder']
                await event.reply(autoresponder, parse_mode = 'html')
    except Exception as e:
        traceback.print_exc()


async def main():
    try:
        await client.start(PHONE_NUMBER)
        logger.info('Бот запущен')
        await client.run_until_disconnected()
    except Exception as e:
        traceback.print_exc()
    finally:
        await client.disconnect()
        logger.exception('Бот остановлен')





def get():
    try:
        #logger.info('Запущен get')
        mydb = bd_connect()
        cursor = mydb.cursor(dictionary=True)
        sql = f"SELECT * FROM autosend"
        cursor.execute(sql, )
        rows = cursor.fetchall()
        mydb.commit()
        cursor.close()
        mydb.close()
        #logger.info(rows)
    except Exception as e:
        logger.exception(f'Ошибка: {e}')
    else:
        #logger.info(f'Получена информация ')
        return rows[0] if rows else None



def bd_connect():
    k = 0
    while k <= 5:
        try:
            mydb = mysql.connector.connect(
                host='HOST',
                user='USER',
                port='PORT',
                password='PASSWORD',
                database='DATEBASE'
            )
        except mysql.connector.Error as err:
            logger.exception(f"Ошибка подключения к базе данных: {err}")
            k += 1
        else:
            #logger.info('Успешное подключение к БД')
            return mydb
    return None

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен пользователем')
    except Exception as e:
        traceback.print_exc()