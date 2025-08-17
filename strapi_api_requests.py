import requests
from environs import env

AUTH_TOKEN = env("AUTH_TOKEN")
HEADERS = {
    'Authorization': f'Bearer {AUTH_TOKEN}',
    'Content-Type': 'application/json'
}


def get_goods():
    url = 'http://localhost:8000/api/products'
    goods = requests.get(url=url, headers=HEADERS)
    goods.raise_for_status()
    goods = goods.json()['data']
    return goods


def get_product(id):
    url = f'http://localhost:8000/api/products/{id}?populate=picture'
    product = requests.get(url=url, headers=HEADERS)
    product.raise_for_status()
    product = product.json()['data']
    return product


def is_cart_exist(tg_id):
    url = f'http://localhost:8000/api/carts?filters[tg_id][$eq]={tg_id}'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    if response.json()['data']:
        return True
    else:
        return False


def is_user_exist(user_email, username):
    url = f'http://localhost:8000/api/users?filters[$or][0][email][$eq]={user_email.lower()}&filters[$or][1][username][$eq]={username}'
    response = requests.get(url, headers=HEADERS)

    response.raise_for_status()
    if response.json():
        return True
    else:
        return False


def create_cart(tg_id):
    if not is_cart_exist(tg_id):
        data = {
            "data": {
                "tg_id": tg_id
            }
        }
        url = 'http://localhost:8000/api/carts'
        response = requests.post(url, json=data, headers=HEADERS)
        response.raise_for_status()
        return response.json()


def get_cart(tg_id):
    url = f'http://localhost:8000/api/carts?filters[tg_id][$eq]={tg_id}&populate[0]=cart_products&populate[1]=cart_products.product'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    cart = response.json()['data'][0]
    return cart


def add_product_to_cart(tg_id, product_id):
    cart = get_cart(tg_id)
    cart_id = cart['id']

    url = f'http://localhost:8000/api/cart-products'
    response_get = requests.get(url, headers=HEADERS)
    response_get.raise_for_status()

    data = {
        "data": {
            "product": product_id,
            "quantity": 2,
            "cart": cart_id
        }
    }

    response_put = requests.post(url, json=data, headers=HEADERS)
    response_put.raise_for_status()


def remove_product_from_cart(cart_product_id):
    url = f'http://localhost:8000/api/cart-products/{cart_product_id}'
    response = requests.delete(url, headers=HEADERS)
    response.raise_for_status()


def create_or_update_user_profile(user_email, username):
    if not is_user_exist(user_email, username):
        url = f'http://localhost:8000/api/users'

        data = {
            "username": username,
            "email": user_email,
            "password": "default"
        }

        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()
    else:
        url = f'http://localhost:8000/api/users?filters[$or][0][email][$eq]={user_email.lower()}&filters[$or][1][username][$eq]={username}'

        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        profile_username = response.json()[0]['username']
        profile_email = response.json()[0]['email']
        profile_id = response.json()[0]['id']
        if profile_username != username or profile_email != user_email:
            url = f'http://localhost:8000/api/users/{profile_id}'
            data = {
                "username": username,
                "email": user_email
            }

            response = requests.put(url, headers=HEADERS, json=data)
            response.raise_for_status()
            return response.json()
        else:
            return response.json()[0]


def pay_cart(profile_id, cart_id):
    url = f'http://localhost:8000/api/users/{profile_id}'
    data = {
        "carts": cart_id
    }
    response_get = requests.put(url, headers=HEADERS, json=data)
    response_get.raise_for_status()
