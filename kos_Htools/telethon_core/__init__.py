from typing import Union
"""
kos_Htools.telethon_core - Модуль для работы с Telegram API
"""

from .clients import MultiAccountManager, create_multi_account_manager, get_multi_manager
from .settings import TelegramAPI
from .config import Config

__all__ = [
    "MultiAccountManager",
    "TelegramAPI",
    "Config",
    "create_multi_account_manager",
    "get_multi_manager"
] 