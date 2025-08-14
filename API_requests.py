import requests
from environs import env


def get_goods():
    url = 'http://localhost:8000/api/products'
    auth_token = env("AUTH_TOKEN")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    goods = requests.get(url=url, headers=headers)
    goods.raise_for_status()
    goods = goods.json()['data']
    return goods


def get_product(id):
    url = f'http://localhost:8000/api/products/{id}?populate=picture'
    auth_token = env("AUTH_TOKEN")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    product = requests.get(url=url, headers=headers)
    product.raise_for_status()
    product = product.json()['data']
    return product


def is_cart_exist(tg_id):
    auth_token = env("AUTH_TOKEN")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    url = f'http://localhost:8000/api/carts?filters[tg_id][$eq]={tg_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    if response.json()['data']:
        return True
    else:
        return False


def is_user_exist(user_email):
    auth_token = env("AUTH_TOKEN")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    url = f'http://localhost:8000/api/users?filters[email][$eq]={user_email.lower()}'
    response = requests.get(url, headers=headers)

    response.raise_for_status()
    if response.json():
        return True
    else:
        return False


def create_cart(tg_id):
    if not is_cart_exist(tg_id):
        auth_token = env("AUTH_TOKEN")
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "data": {
                "tg_id": tg_id,
                "id": tg_id,
            }
        }
        url = 'http://localhost:8000/api/carts'
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()


def add_product_to_cart(tg_id, product_id):
    auth_token = env("AUTH_TOKEN")

    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }

    url = f'http://localhost:8000/api/cart-products'
    response_get = requests.get(url, headers=headers)
    response_get.raise_for_status()

    data = {
        "data": {
            "product": product_id,
            "quantity": 2,
            "cart": tg_id
        }
    }

    response_put = requests.post(url, json=data, headers=headers)
    response_put.raise_for_status()


def get_cart(tg_id):
    auth_token = env("AUTH_TOKEN")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }

    url = f'http://localhost:8000/api/carts?filters[tg_id][$eq]={tg_id}&populate[0]=cart_products&populate[1]=cart_products.product'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart = response.json()['data'][0]
    return cart


def remove_product_from_cart(product_id):
    auth_token = env("AUTH_TOKEN")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }

    url = f'http://localhost:8000/api/cart-products/{product_id}'
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def create_user_profile(user_email, username):
    auth_token = env("AUTH_TOKEN")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    if not is_user_exist(user_email):
        url = f'http://localhost:8000/api/users'

        data = {
            "username": username,
            "email": user_email,
            "password": "default"
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    else:
        url = f'http://localhost:8000/api/users?filters[email][$eq]={user_email.lower()}'

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()[0]


def pay_cart(profile_id, cart_id):
    auth_token = env("AUTH_TOKEN")

    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }

    url = f'http://localhost:8000/api/users/{profile_id}'

    data = {
        "carts": cart_id
    }

    response_get = requests.put(url, headers=headers, json=data)
    response_get.raise_for_status()
