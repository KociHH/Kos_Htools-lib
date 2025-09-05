import asyncio
import logging
import os
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError
from itertools import cycle
from typing import Union
logger = logging.getLogger(__name__)

class MultiAccountManager:
    def __init__(
            self,
            accounts_data: dict[str, Union[str, int]],
            system_version: str | None = "Windows 10",
            device_model: str | None = "PC 64bit"
            ):
        
        self.accounts_data = accounts_data
        self.clients = {}
        self.client_cycle = None
        self.current_client = None
        
        self.system_version = system_version
        self.device_model = device_model

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
            proxy: tuple = account.get('proxy')
            session_file = f'session_{phone_number}.session'
            
            if phone_number in self.clients.keys():
                logger.info(f"Аккаунт {phone_number} уже запущен")
                continue
                     
            client = TelegramClient(
                session=f'session_{phone_number}',
                api_id=api_id,
                api_hash=api_hash,
                device_model=self.device_model,
                system_version=self.system_version,
                proxy=proxy
                )
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


    async def get_or_switch_client(self, phone_session: str | None = None, switch: bool = False):
        if not self.clients:
            logger.error("Нет подключенных клиентов!")
            return None
        
        if phone_session and phone_session in self.clients.keys():
            self.current_client = self.clients[phone_session]
            logger.info(f'Выбран клиент: session_{phone_session}')
            return self.current_client
        
        elif phone_session and phone_session not in self.clients:
            logger.warning(
                f'Клиент с номером {phone_session} не найден.\n'
                f'Доступные номера: {list(self.clients.keys())}.\n'
                'Будет выбран следующий доступный клиент.'
            )
            switch = True
        
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
            logger.error(f'Ошибка в функции cycle_clients: \n {e}')
            self.client_cycle = None
            return None
            

def create_multi_account_manager():
    from .settings import TelegramAPI
    data_telethon = TelegramAPI().create_json()
    return MultiAccountManager(data_telethon)


multi: MultiAccountManager | None = None

def get_multi_manager() -> MultiAccountManager:
    global multi
    if multi is None:
        multi = create_multi_account_manager()
    return multi