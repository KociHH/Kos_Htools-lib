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
from kos_Htools.telethon_core import multi, create_custom_manager
from kos_Htools.telethon_core.utils.parse import UserParse
import asyncio

async def main():
    # Способ 1: Использование предварительно созданного экземпляра multi
    # (Использует данные из .env файла)
    client = await multi()
    
    # Способ 2: Создание пользовательского менеджера с собственными данными
    accounts_data = [
        {
            "api_id": 123456,
            "api_hash": "your_api_hash",
            "phone_number": "+1234567890",
            "proxy": None  # Можно указать прокси в формате tuple
        }
    ]
    custom_multi = create_custom_manager(
        accounts_data,
        system_version="Windows 10",  # Опционально
        device_model="PC 64bit"       # Опционально
    )
    custom_client = await custom_multi()

    # Парсинг пользователей
    parser = UserParse(client, {'chats': ['https://t.me/groupname']})
    user_ids = await parser.collect_user_ids()
    
    # Анализ сообщений пользователей
    messages = await parser.collect_user_messages(limit=100, sum_count=True)
    
    # Закрытие клиентов после использования
    await multi.stop_clients()
    await custom_multi.stop_clients()

if __name__ == '__main__':
    asyncio.run(main())
```

### Полный пример работы с парсингом пользователей

```python
from kos_Htools.telethon_core import multi
from kos_Htools.telethon_core.utils.parse import UserParse
import asyncio
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # Получение клиента Telegram
    client = await multi()
    
    # Пример парсинга ID пользователей из чата
    chat_data = {'chats': ['https://t.me/example_chat']}
    parser = UserParse(client, chat_data)
    
    # Получение ID пользователей
    user_ids = await parser.collect_user_ids()
    if user_ids:
        logger.info(f"Собрано {sum(len(ids) for ids in user_ids.values())} ID пользователей")
        
    # Пример анализа сообщений пользователей
    messages = await parser.collect_user_messages(limit=200, sum_count=True)
    if messages:

        # Топ 5 активных пользователей
        top_users = sorted(
            messages.items(), 
            key=lambda x: x[1].get('total_messages', 0), 
            reverse=True
        )[:5]
        
        logger.info("Топ 5 активных пользователей:")
        for user_id, data in top_users:
            logger.info(f"Пользователь {user_id}: {data.get('total_messages', 0)} сообщений")
    
    # Закрытие клиентов
    await multi.stop_clients()
    
    return user_ids, messages

if __name__ == '__main__':
    asyncio.run(main())
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

### SQLAlchemy DAO

В библиотеке реализован универсальный асинхронный слой доступа к данным (DAO) для работы с SQLAlchemy.

#### Пример использования

```python
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from my_models import User  # Ваша модель SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession

dao = BaseDAO(User, db_session)  # db_session — экземпляр AsyncSession

# Получить одного пользователя или сделать условие
user = await dao.get_one(User.user_id == 123456)
if user:
    ...
else:
    ...

# Создать пользователя
new_user = await dao.create({'name': 'Иван', 'age': 30})

# Обновить пользователя (отследить) - авто
await dao.update(User.id == 1, {'name': 'Петр', 'age': 31})
```

#### Описание классов

- **BaseDAO** — базовый класс для CRUD-операций.
- **Update_date** — вспомогательный класс для обновления и логирования изменений в объекте.



## Требования

- Python 3.10+
- Telethon
- Redis
- SQLAlchemy
- python-dotenv 