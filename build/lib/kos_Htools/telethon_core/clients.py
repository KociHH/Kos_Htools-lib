import asyncio
import logging
import os
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError
from telethon_core.settings import TelegramAPI
from itertools import cycle
logger = logging.getLogger(__name__)

class MultiAccountManager:
    def __init__(self, accounts_data):
        self.accounts_data = accounts_data
        self.clients = {}
        self.client_cycle = None
        self.current_client = None

    async def __call__(self):
        if not self.clients:
            await self.start_clients()
        return await self.get_or_switch_client()
    
    async def start_clients(self):
        if not self.accounts_data or len(self.accounts_data) == 0 or \
        any(not account.get('api_id') or not account.get('api_hash') or not account.get('phone_number') \
            for account in self.accounts_data):
            logger.error('Словари в списке пусты, telethon не запущен!')
            return
        
        i = 0
        for account in self.accounts_data:
            api_id = account.get("api_id")
            api_hash = account.get("api_hash")
            phone_number = account.get("phone_number")
            session_file = f'session_{phone_number}.session'
            
            if phone_number in self.clients.keys():
                logger.info(f"Аккаунт {phone_number} уже запущен")
                continue
                     
            client = TelegramClient(f'session_{phone_number}', api_id, api_hash)
            try:
                if os.path.exists(session_file):
                    await client.connect()
                    if not await client.is_user_authorized():
                        logger.warning(f'Сессия не валидна {session_file} (нужна авторизация)')
                        await client.start(phone_number)
                else:
                    await client.start(phone_number)
                        
                logger.info(f"Аккаунт {phone_number} подключен")
                self.clients[phone_number] = client
                i += 1
                logger.info(f'Запущен новый клиент: {i}!')

            except FloodWaitError as e:
                logger.warning(f"Слишком много запросов.. Ждём {e.seconds} секунд..")
                await asyncio.sleep(e.seconds)
                await client.start(phone_number)
            except Exception as e:
                logger.error(f"Ошибка при подключении: {e}")
                continue
                
        logger.info(f'Кол-во запущенных клиентов: {len(self.clients.keys())}')
        if self.clients:
            self.cycle_clients()


    async def get_or_switch_client(self, switch: bool = False):
        if not self.clients:
            logger.error("Нет подключенных клиентов!")
            return None
        
        if not self.client_cycle:
            self.client_cycle = cycle(self.clients.values())

        if switch or self.current_client is None:
            self.current_client = next(self.client_cycle, None)
            
        return self.current_client
    
    
    async def stop_clients(self):
        count = 0
        for phone_number, client in self.clients.items():
            try:
                await client.disconnect()
                logger.info(f"Отключен клиент {phone_number}")
                count += 1
            except Exception as e:
                logger.error(f"Ошибка при отключении клиента {phone_number}: {e}")
        logger.info(f'Все клиенты были отключены: {count} всего')
        
        
    def cycle_clients(self):
        try:
            self.client_cycle = cycle(self.clients.values())
            return self.client_cycle
        except Exception as e:
            logger.error(f'Не перепрал в функции cycle_clients: \n {e}')
            
data_telethon = TelegramAPI().create_json()
multi = MultiAccountManager(data_telethon)