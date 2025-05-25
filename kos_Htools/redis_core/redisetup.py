import json
import logging
from typing import Union, Dict, List
from redis import Redis

logger = logging.getLogger(__name__)

class RedisBase:
    def __init__(self, key: str, data: Union[Dict, List], redis: Redis = Redis()):
        self.redis = redis
        self.key = key
        self.data = data
    
    def cached(self, data: Union[Dict, List], key: str | None = None, ex: int | None = None) -> None:   
        key = key or self.key
        
        if isinstance(data, (dict, list)):
            data = json.dumps(data)
            
        try:
            self.redis.set(name=key, value=data, ex=ex)
        except Exception as e:
            logger.error(f'Ошибка в redis: {e}')
    
    def get_default_value(self, data_type: type) -> Union[Dict, List]:
        return {} if data_type == dict else []
    
    def get_cached(self, key: str | None = None, data_type: type | None = None) -> Union[Dict, List, str, bytes]:
        key = key or self.key
        data_type = data_type or type(self.data)
        result = self.get_default_value(data_type)

        try:
            cached_data = self.redis.get(key)
            if not cached_data:
                logger.warning(f'Ключ не найден: {key}')
                return result

            decode_data = cached_data.decode('utf-8')
            if data_type in (dict, list):
                try:
                    return json.loads(decode_data)
                except json.JSONDecodeError:
                    logger.error(f'Ошибка декодирования JSON для ключа: {key}')
                    return result
            else:
                return decode_data
            
        except Exception as e:
            logger.error(f'Ошибка получения данных: {e}')
            return result   

    def delete_key(self, key: str | None = None) -> None:
        key = key or self.key
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error(f'Ошибка удаления ключа {key}: {e}')

