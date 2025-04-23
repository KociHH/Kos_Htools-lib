# kos_Htools

Комплексная библиотека для работы с Telegram и Redis.

## Установка

```bash
pip install kos_Htools
```

## Компоненты

Библиотека включает два основных модуля:

### 1. Telethon Tools

Инструменты для работы с Telegram API:
- Поддержка множественных аккаунтов
- Парсинг пользователей из чатов и каналов
- Анализ сообщений
- Автоматическая работа с привязанными группами

### 2. Redis Tools

Инструменты для работы с Redis:
- Кэширование данных
- Сериализация/десериализация JSON
- Работа с ключами и значениями

## Настройка

1. Создайте файл `.env` в корневой директории вашего проекта
2. Добавьте следующие переменные:

```
TELEGRAM_API_ID=ваш_api_id
TELEGRAM_API_HASH=ваш_api_hash
TELEGRAM_PHONE_NUMBER=ваш_номер_телефона
```

Так же можно добавить proxy для каждой сессии например:
```
TELEGRAM_PROXY=socks5:ip:port:username:password 

Другой формат добавления:   
socks5:ip:port
http:ip:port
```

Для работы с несколькими аккаунтами, разделите значения через запятую:
```
TELEGRAM_API_ID=id1,id2,id3
TELEGRAM_API_HASH=hash1,hash2,hash3
TELEGRAM_PHONE_NUMBER=phone1,phone2,phone3
```

## Примеры использования

### Telegram Tools

```python
from kos_Htools import MultiAccountManager, TelegramAPI, UserParse
import asyncio

async def main():
    # Инициализация менеджера аккаунтов
    data_telethon = TelegramAPI().create_json()
    multi = MultiAccountManager(data_telethon) # можно добавить system_version, device_model или скипнуть
    client = await multi()
    
    # Парсинг пользователей
    parser = UserParse(client, {'chats': ['https://t.me/groupname']})
    user_ids = await parser.collect_user_ids()
    
    # Парсер кол-во сообщений в чатах у user
    messages = await parser.collect_user_messages(limit=100, sum_count=True)
```

### Redis Tools

```python
from kos_Htools import RedisBase
import redis

# Создание Redis клиента
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Кэширование данных
redis_base = RedisBase(key="my_key", data={"example": "data"}, redis=redis_client)
redis_base.cached(ex=3600)  # ex - время жизни кэша в секундах

# Получение данных
cached_data = redis_base.get_cached()
```

## Требования

- Python 3.6+
- Telethon
- Redis
- python-dotenv 