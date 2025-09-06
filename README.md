# kos_Htools

Комплексная библиотека для работы с Telegram, Redis, Sqlalchemy.

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
from kos_Htools.telethon_core import multi, create_custom_manager, get_multi_manager
from kos_Htools.telethon_core.utils.parse import UserParse
import asyncio

async def main():
    # Способ 1: Использование предварительно созданного экземпляра multi
    # (Использует данные из .env файла)
    manager = get_multi_manager()
    client = await manager()
    
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
    await manager.stop_clients()
    await custom_multi.stop_clients()

if __name__ == '__main__':
    asyncio.run(main())

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
    manager = get_multi_manager()
    client = await manager()
    
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
    await manager.stop_clients()
    
    return user_ids, messages

if __name__ == '__main__':
    asyncio.run(main())
```

### Redis Tools

#### RedisBase - Упрощенная работа с JSON данными

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

#### RedisShortened - Специализированная работа со списками

> **Рекомендация:** Для работы со списками используйте `RedisShortened` вместо `RedisBase`.
> 
> **Важно:** При работе со списковыми операциями, методы `lrange`, `llen`, `lrem` (и опционально `lpush`, `rpush`) выполняют внутреннюю проверку типа ключа через `check_key_list()`. Эта функция гарантирует, что ключ Redis действительно является списком, предотвращая ошибки при попытке выполнения списковых операций на ключах другого типа.

##### Ниже представленны функции которые есть в официальной [документации Redis](https://redis.io/docs/). 

```python
from kos_Htools.redis_core.redisetup import RedisShortened
import redis

# Создание Redis клиента
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Работа со списками
redis_list = RedisShortened(key="my_list", data=[], redis=redis_client)

# Добавление элементов в начало списка
redis_list.lpush("item1", "item2", "item3")

# Добавление элементов в конец списка
redis_list.rpush("item4", "item5")

# Получение и удаление элемента с начала списка
first_item = redis_list.lpop()

# Получение и удаление элемента с конца списка
last_item = redis_list.rpop()

# Получение диапазона элементов (с 0 по 2)
items = redis_list.lrange(0, 2)

# Получение длины списка
length = redis_list.llen()

# Удаление элемента из списка
count = 1 # Удалить одно вхождение значения
value = "item1"
redis_list.lrem(count, value)
```

#### Описание методов RedisShortened

| Метод | Описание |
|-------|----------|
| `lpush(*values)` | Добавить элементы в начало списка |
| `rpush(*values)` | Добавить элементы в конец списка |
| `lpop()` | Получить и удалить элемент с начала списка |
| `rpop()` | Получить и удалить элемент с конца списка |
| `lrange(start, end, decode=True)` | Получить диапазон элементов. Если `decode=True` (по умолчанию), элементы будут декодированы из байтов. |
| `llen()` | Получить длину списка |
| `lrem(count, value)` | Удалить `count` вхождений `value` из списка. |
| `check_key_list()` | **Вспомогательный метод:** Проверяет, является ли текущий ключ Redis списком. Важно для обеспечения корректности операций. |

### SQLAlchemy DAO

В библиотеке реализован универсальный асинхронный слой доступа к данным (DAO) для работы с SQLAlchemy.

#### Пример использования

```python
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from my_models import User  # Ваша модель SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession

dao = BaseDAO(User, db_session)  # db_session — экземпляр AsyncSession

# Получить одну запись по условию
user = await dao.get_one(User.user_id == 123456)

# Создать новую запись
new_user = await dao.create({'name': 'Иван', 'age': 30})

# Обновить запись
await dao.update(User.id == 1, {'name': 'Петр', 'age': 31})

# Получить все значения столбца
names = await dao.get_all_column_values(User.name)

# Получить все записи
all_users = await dao.get_all()

# Обнулить атрибуты 'name' и 'age' для ВСЕХ пользователей, у которых is_active == True
await dao.null_objects(attrs_null=['name', 'age'], where=User.is_active == True)

# Получить одного пользователя по имени, сортируя по ID в порядке убывания (для дубликатов)
user_ordered = await dao.get_one_ordered_or_none(User.name == 'Иван', User.id.desc())
if user_ordered:
    print(f"Найден пользователь: {user_ordered.name} с ID: {user_ordered.id}")

# Получить все имена для пользователей с id 123456 (один столбец)
alice_cities = await dao.get_all_column_values(User.name, User.name == 123456)
print(f"Имена: {alice_cities}")

# Получить имена и дату для пользователей с id 123456 (несколько столбцов)
alice_names_ages = await dao.get_all_column_values((User.name, User.date), User.name == 123456)
print(f"Имена и даты: {alice_names_ages}")
```

#### Описание методов BaseDAO

- **get_one(where)** — получить одну запись по условию (или None).
- **create(data)** — создать новую запись из словаря.
- **update(where, data)** — обновить запись по условию.
- **get_all_column_values(columns, where)** — получить список значений из одного или нескольких столбцов, опционально фильтруя по условию. Возвращает список значений (для одного столбца) или список кортежей (для нескольких столбцов).
- **get_all()** — получить все записи модели.
- **delete(where)** — удалить записи по условию.
- **null_objects(attrs_null, where)** — обнуляет значения заданных атрибутов во **ВСЕХ** записях, удовлетворяющих условию.
- **get_one_ordered_or_none(where, order_by_clause)** — получить один объект модели по условию, используя сортировку.

## Утилиты

### DateTemplate - Работа со временем (Московское время)

Класс `DateTemplate` предоставляет удобные методы для получения текущей даты и времени в Московском часовом поясе, а также для создания пользовательских дат.

#### Пример использования

```python
from kos_Htools import DateTemplate

# Создание экземпляра класса
date_helper = DateTemplate()

# Получение текущей даты (объект date)
current_date = date_helper.conclusion_date(option='date')
print(f"Текущая дата: {current_date}")

# Получение времени в строковом формате (Дата: DD.MM.YYYY, Время: HH:MM)
time_info = date_helper.conclusion_date(option='time_info_style_str')
print(f"Информация о времени: \n{time_info}")

# Получение даты и времени в строковом формате (DD.MM.YYYY HH:MM)
datetime_str = date_helper.conclusion_date(option='time_and_date_str')
print(f"Дата и время (строка): {datetime_str}")

# Получение текущего времени (объект datetime без микросекунд)
current_time_obj = date_helper.conclusion_date(option='time_now')
print(f"Текущее время (объект): {current_time_obj}")

# Получение текущего времени в формате Unix timestamp (целое число)
timestamp_int = date_helper.conclusion_date(option='fromtimestamp')
print(f"Timestamp: {timestamp_int}")

# Создание пользовательской даты/времени с добавлением интервалов
# Добавление 1 дня и 2 часов к текущему времени
custom_dt_added = date_helper.custom_date(add_time={'day': 1, 'hour': 2})
print(f"Измененная дата (добавлено 1 день 2 часа): {custom_dt_added}")

# Получение текущей даты/времени без изменений (custom_date без аргументов)
current_dt_dict = date_helper.custom_date(add_time=None)
print(f"Текущая дата (словарь): {current_dt_dict}")

# Важное замечание для сохранения в базы данных:
# Если вы используете SQLAlchemy с колонками типа DateTime без поддержки временных зон,
# всегда убирайте информацию о временной зоне перед сохранением:
# например: date_obj.replace(tzinfo=None)
```

#### Описание методов DateTemplate

- **`conclusion_date(option: str)`**
  Получает информацию о дате и времени в различных форматах в Московском часовом поясе.
  - `option='date'`: Возвращает текущую дату как объект `datetime.date`.
  - `option='time_info_style_str'`: Возвращает форматированную строку "Дата: DD.MM.YYYY\nВремя: HH:MM".
  - `option='time_and_date_str'`: Возвращает форматированную строку "DD.MM.YYYY HH:MM".
  - `option='time_now'`: Возвращает текущее время как объект `datetime.datetime` (без микросекунд).
  - `option='fromtimestamp'`: Возвращает текущий Unix timestamp (целое число).
  - В случае неизвестного `option` вызывает `ValueError`.

- **`custom_date(add_time: dict | None)`**
  Позволяет получить текущую дату и время (или модифицированную) в виде словаря.
  - `add_time`: Словарь, содержащий интервалы для добавления к текущему времени (например, `{'year': 1, 'month': 2, 'day': 3, 'hour': 4, 'minute': 5, 'second': 6}`). Необязательно.
  - Возвращает словарь с компонентами года, месяца, дня, часа, минуты и секунды.

## Требования

- Python 3.10+
- Telethon
- Redis
- SQLAlchemy
- python-dotenv 
- pytz 