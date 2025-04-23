"""
kos_Htools - Библиотека инструментов для работы с Telegram и Redis
"""

from .telethon_core.clients import MultiAccountManager
from .telethon_core.settings import TelegramAPI
from .redis_core.redisetup import RedisBase

__version__ = "0.1.1"
__all__ = ["MultiAccountManager", "TelegramAPI", "RedisBase"]