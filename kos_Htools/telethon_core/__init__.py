from typing import Union
"""
kos_Htools.telethon_core - Модуль для работы с Telegram API
"""

from .clients import MultiAccountManager, create_multi_account_manager

multi = create_multi_account_manager()

def create_custom_manager(accounts_data: list[dict[str, Union[str, int, tuple]]], system_version: str ="Windows 10", device_model: str ="PC 64bit"):
    return MultiAccountManager(accounts_data, system_version, device_model)

__all__ = ["MultiAccountManager", "multi", "create_custom_manager"] 