import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @staticmethod
    def get_api_data():
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
        
        if not all([api_id, api_hash, phone_number]):
            raise ValueError("Необходимо установить переменные окружения TELEGRAM_API_ID, TELEGRAM_API_HASH и TELEGRAM_PHONE_NUMBER")
            
        return api_id, api_hash, phone_number 