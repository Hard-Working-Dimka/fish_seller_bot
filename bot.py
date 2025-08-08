import redis
import requests
from environs import env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from telegram.ext import Filters, Updater, CallbackContext
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

_database = None


def get_goods():
    url = 'http://localhost:8000/api/products'
    auth_token = env("AUTH_TOKEN")
    headers = {'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'}
    goods = requests.get(url=url, headers=headers)
    goods = goods.json()['data']
    return goods


def get_product(id):
    url = f'http://localhost:8000/api/products/{id}'
    auth_token = env("AUTH_TOKEN")
    headers = {'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'}
    product = requests.get(url=url, headers=headers)
    product = product.json()['data']
    return product


def start(update, context):
    goods = get_goods()
    keyboard = []

    for product in goods:
        button = [InlineKeyboardButton(product['attributes']['title'], callback_data=product['id'])]
        keyboard.append(button)

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_menu(update, context):
    query = update.callback_query

    query.answer()
    product = get_product(query.data)
    product_description = product['attributes']['description']

    update.callback_query.message.edit_text(product_description)

    return 'HANDLE_MENU'


def handle_users_reply(update, context):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = env('DATABASE_PASSWORD')
        database_host = env('DATABASE_HOST')
        database_port = env('DATABASE_PORT')
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    env.read_env()

    token = env('TELEGRAM_TOKEN')
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()
