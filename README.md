# Телеграм бот по продаже рыбы

<!-- TOC -->

* [Телеграм бот по продаже рыбы](#телеграм-бот-по-продаже-рыбы)
    * [Требования](#требования)
    * [Окружение](#окружение)
        * [Зависимости](#зависимости)
        * [Переменные окружения](#переменные-окружения)
    * [Установка и запуск Strapi](#установка-и-запуск-strapi)
    * [Запуск](#запуск)
    * [Цели проекта](#цели-проекта)

<!-- TOC -->

## Требования

- Python 3.9+
- Установленные зависимости из `requirements.txt`
- NodeJS == 16.16.0

## Окружение

### Зависимости

Скачайте код с GitHub. Затем установите зависимости

```sh
pip install -r requirements.txt
```

### Переменные окружения

Установите переменные окружения в файле `.env`

```bash
AUTH_TOKEN=<strapi>
DATABASE_PASSWORD=<redis>
DATABASE_HOST=<redis>
DATABASE_PORT=<redis>
TELEGRAM_TOKEN=<telegram>
API_BASE_URL=<strapi base urll> - по умолчанию: `http://localhost:1337`
```

## Установка и запуск Strapi

Установите [Node.js](https://nodejs.org/en/). **Версия NodeJS == 16.16.0!**

Далее необходимо по документации
установить [CMS (Strapi)](https://github.com/strapi/strapi?tab=readme-ov-file#-installation) согласно версии NodeJS.

Согласно [документации](https://docs.strapi.io/cms/installation/cli) запустите CMS.

Используйте команду

```bash
npm run build  
```

Перейдите в админку, по предложенному в терминале адресу и зарегистрируйтесь.

Теперь необходимо создать модели:

**Cart**

<img width="1191" height="527" alt="image" src="https://github.com/user-attachments/assets/fd40122e-ab35-4fca-b183-3cea380bef56" />

* Связь users_permissions_user - User has many Carts
* Связь cart_products - Cart belongs to many CartProducts

**CartProduct**

<img width="831" height="527" alt="image" src="https://github.com/user-attachments/assets/6093d013-3ca7-4822-95bf-91c77ee4eb39" />

* Связь с cart - Cart has many CartProducts.
* Связь с product - Product has many CartProducts

**Product**

<img width="948" height="798" alt="image" src="https://github.com/user-attachments/assets/8c1d5f50-d814-485c-b5b1-a69bec977eae" />

* Связь cart_products - Product belongs to many CartProducts

## Запуск

Запустите бота, предварительно запустив сервер CMS:

```sh
python3 bot.py
```

## Цели проекта

Код написан в учебных целях.
