# Телеграм бот по продаже рыбы

## Требования

- Python 3.9+
- Установленные зависимости из `requirements.txt`
- NodeJS == 16.16.0

## Как запустить

Для запуска сайта вам понадобится Python третьей версии.

Скачайте код с GitHub. Затем установите зависимости

```sh
pip install -r requirements.txt
```

Установите переменные окружения в файле `.env`

```bash
AUTH_TOKEN=<strapi>
DATABASE_PASSWORD=<redis>
DATABASE_HOST=<redis>
DATABASE_PORT=<redis>
TELEGRAM_TOKEN=<telegram>
API_BASE_URL=<strapi base urll> - по умолчанию: `http://localhost:1337`
```

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

**CartProduct**

**Product**

Запустите бота, предварительно запустив сервер CMS:

```sh
python3 bot.py
```

## Цели проекта

Код написан в учебных целях.