import logging
from .utils.dataclasses import TelethonLog
from .config import Config
from .utils.other import format_proxy_string

logger = logging.getLogger(__name__)

class TelegramAPI:
    def __init__(self):
        self.api_id, self.api_hash, self.phone_number, self.proxy = Config.get_api_data()
    
    def create_json(self) -> list:     
        if not (self.api_id and self.api_hash and self.phone_number):
            logger.error("Переменные окружения не найдены или пустые!")
            return []
        
        api_ids = self.api_id.split(',') if ',' in self.api_id else [self.api_id]
        api_hashes = self.api_hash.split(',') if ',' in self.api_hash else [self.api_hash]
        phone_numbers = self.phone_number.split(',') if ',' in self.phone_number else [self.phone_number]
        
        proxies = []
        if self.proxy:
            proxy_strings = self.proxy.split(',') if ',' in self.proxy else [self.proxy]
            if len(proxy_strings) != len(api_ids):
                logger.error(f"Количество прокси ({len(proxy_strings)}) не совпадает с количеством API ID ({len(api_ids)})!")
                return []

            for proxy_str in proxy_strings:
                proxy_tuple = format_proxy_string(proxy_str.strip())
                proxies.append(proxy_tuple)
        else:
            proxies = [None] * len(api_ids)
        
        accounts = []
        for i in range(len(api_ids)):
            try:
                account = {
                    "api_id": int(api_ids[i].strip()),
                    "api_hash": api_hashes[i].strip(),
                    "phone_number": phone_numbers[i].strip(),
                    "proxy": proxies[i],
                }
                accounts.append(account)
            except ValueError:
                logger.error(f"Ошибка в данных аккаунта {i + 1}. Проверь api_id (должно быть число).")

        Log = TelethonLog(self.api_id, self.api_hash, self.phone_number, self.proxy)
        logger.info(Log.return_self())
        return accounts