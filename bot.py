import redis
import requests
from API_requests import *
from environs import env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from io import BytesIO

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

_database = None


def start(update, context):
    update.message.reply_text(text='Привет! Ты в рыбном магазине!')

    return 'HANDLE_MENU'


def handle_menu(update, context):
    goods = get_goods()
    keyboard = []

    for product in goods:
        button = [InlineKeyboardButton(product['attributes']['title'], callback_data=product['id'])]
        keyboard.append(button)

    keyboard.append([InlineKeyboardButton('Моя корзина', callback_data='cart')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.effective_message.reply_text('Please choose:', reply_markup=reply_markup)

    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton('Назад', callback_data='menu')],
        [InlineKeyboardButton('Добавить в корзину', callback_data=f'add_to_cart_{query.data}')],
        [InlineKeyboardButton('Моя корзина', callback_data='cart')],
    ]

    if query.data.startswith('add_to_cart_'):
        product_id = query.data.split('_')[-1]
        create_cart(query.from_user.id)
        add_product_to_cart(query.from_user.id, product_id)
        next_handle = handle_menu(update, context)
        return next_handle

    if query.data == 'cart':
        handle_cart(update, context)
        return 'HANDLE_CART'

    product = get_product(query.data)
    image_url = product['attributes']['picture']['data'][0]['attributes']['url']
    response = requests.get(f'http://localhost:8000{image_url}')
    response.raise_for_status()
    image_data = BytesIO(response.content)
    product_description = product['attributes']['description']
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_photo(caption=product_description, photo=image_data, reply_markup=reply_markup)


def handle_cart(update, context):
    keyboard = []
    query = update.callback_query

    if query.data.startswith('del_'):
        product_id = query.data.split('_')[-1]
        remove_product_from_cart(product_id)
        query.data = 'updated_cart'
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        handle_cart(update, context)
        return 'HANDLE_CART'

    if query.data == 'pay':
        context.bot.send_message(chat_id=query.from_user.id, text='Введите ваш email:')
        return 'HANDLE_WAITING_EMAIL'

    cart = get_cart(query.from_user.id)
    message = []
    if cart['attributes']['cart_products']['data']:
        for product in cart['attributes']['cart_products']['data']:
            product_info = product['attributes']['product']['data']['attributes']
            product_title = product_info['title']
            product_price = product_info['price']
            cart_product_id = product['id']
            button = [InlineKeyboardButton(f'удалить {product_title}', callback_data=f'del_{cart_product_id}')]
            keyboard.append(button)

            message.append(f'{product_title} --- {product_price}')
    else:
        message.append('К сожалению, корзина пуста.')
    keyboard.append([InlineKeyboardButton('В меню', callback_data='menu')])
    keyboard.append([InlineKeyboardButton('Оплатить', callback_data='pay')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=query.from_user.id, text='\n\n'.join(message), reply_markup=reply_markup)
    query.answer()


def handle_waiting_email(update, context):
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

    user_email = update.message.text
    username = update.message.from_user.username

    profile = create_or_update_user_profile(user_email, username)
    profile_id = profile['id']

    pay_cart(profile_id, update.message.from_user.id)

    context.bot.send_message(chat_id=update.message.chat_id, text='Заказ успешно создан, ожидайте письмо от менеджера')


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
        'HANDLE_CART': handle_cart,
        'HANDLE_WAITING_EMAIL': handle_waiting_email
    }

    if user_reply == 'menu':
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        user_state = 'HANDLE_MENU'

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
