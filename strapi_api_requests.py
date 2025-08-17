import requests


def get_goods(auth_token, base_url):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    url = f'{base_url}/api/products'
    goods = requests.get(url=url, headers=headers)
    goods.raise_for_status()
    goods = goods.json()['data']
    return goods


def get_product(id, auth_token, base_url):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    params = {'populate': 'picture'}
    url = f'{base_url}/api/products/{id}'
    product = requests.get(url=url, headers=headers, params=params)
    product.raise_for_status()
    product = product.json()['data']
    return product


def is_cart_exist(tg_id, auth_token, base_url):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'filters[tg_id][$eq]': tg_id
    }
    url = f'{base_url}/api/carts'
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    if response.json()['data']:
        return True
    else:
        return False


def is_user_exist(user_email, username, auth_token, base_url):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'filters[$or][0][email][$eq]': user_email.lower(),
        'filters[$or][1][username][$eq]': username
    }
    url = f'{base_url}/api/users'
    response = requests.get(url, headers=headers, params=params)

    response.raise_for_status()
    if response.json():
        return True
    else:
        return False


def create_cart(tg_id, auth_token, base_url):
    data = {
        "data": {
            "tg_id": tg_id
        }
    }
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    url = f'{base_url}/api/carts'
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart(tg_id, auth_token, base_url):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'filters[tg_id][$eq]': tg_id,
        'populate[0]': 'cart_products',
        'populate[1]': 'cart_products.product'
    }
    url = f'{base_url}/api/carts'
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    cart = response.json()['data'][0]
    return cart


def add_product_to_cart(tg_id, product_id, auth_token, base_url):
    cart = get_cart(tg_id, auth_token, base_url)
    cart_id = cart['id']

    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    url = f'{base_url}/api/cart-products'
    response_get = requests.get(url, headers=headers)
    response_get.raise_for_status()

    data = {
        "data": {
            "product": product_id,
            "quantity": 2,
            "cart": cart_id
        }
    }

    response_put = requests.post(url, json=data, headers=headers)
    response_put.raise_for_status()


def remove_product_from_cart(cart_product_id, auth_token, base_url):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    url = f'{base_url}/api/cart-products/{cart_product_id}'
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def create_or_update_user_profile(user_email, username, auth_token, base_url):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    if not is_user_exist(user_email, username, auth_token, base_url):
        url = f'{base_url}/api/users'

        data = {
            "username": username,
            "email": user_email,
            "password": "default"
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    else:
        params = {
            'filters[$or][0][email][$eq]': user_email.lower(),
            'filters[$or][1][username][$eq]': username
        }
        url = f'{base_url}/api/users'

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        profile_username = response.json()[0]['username']
        profile_email = response.json()[0]['email']
        profile_id = response.json()[0]['id']
        if profile_username != username or profile_email != user_email:
            url = f'{base_url}/api/users/{profile_id}'
            data = {
                "username": username,
                "email": user_email
            }

            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        else:
            return response.json()[0]


def pay_cart(profile_id, cart_id, auth_token, base_url):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    url = f'{base_url}/api/users/{profile_id}'
    data = {
        "carts": cart_id
    }
    response_get = requests.put(url, headers=headers, json=data)
    response_get.raise_for_status()
