import redis
import requests
from environs import env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from io import BytesIO

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
    url = f'http://localhost:8000/api/products/{id}?populate=picture'
    auth_token = env("AUTH_TOKEN")
    headers = {'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'}
    product = requests.get(url=url, headers=headers)
    product = product.json()['data']
    return product


def start(update, context):
    update.message.reply_text(text='Привет! Ты в рыбном магазине!')

    return 'HANDLE_MENU'


def handle_menu(update, context):
    goods = get_goods()
    keyboard = []

    for product in goods:
        button = [InlineKeyboardButton(product['attributes']['title'], callback_data=product['id'])]
        keyboard.append(button)

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.effective_message.reply_text('Please choose:', reply_markup=reply_markup)

    if update.callback_query:
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        update.callback_query.answer()

    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    query = update.callback_query
    query.answer()

    product = get_product(query.data)
    image_url = product['attributes']['picture']['data'][0]['attributes']['url']
    response = requests.get(f'http://localhost:8000{image_url}')
    image_data = BytesIO(response.content)
    product_description = product['attributes']['description']

    keyboard = [[InlineKeyboardButton('Назад', callback_data='1')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_photo(caption=product_description, photo=image_data, reply_markup=reply_markup)

    if update.callback_query:
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        update.callback_query.answer()
    return 'HANDLE_MENU'


def handle_users_reply(update, context):
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
        user_state = 'HANDLE_MENU'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
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
