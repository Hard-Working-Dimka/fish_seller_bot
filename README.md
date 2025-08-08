# Телеграм бот по продаже рыбы

### Как запустить

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
```

Запустите бота сервер

```sh
python3 bot.py
```

## Цели проекта

Код написан в учебных целях.