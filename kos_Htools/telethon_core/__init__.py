"""
kos_Htools.telethon_core - Модуль для работы с Telegram API
"""
from .settings import TelegramAPI
from .config import Config

__all__ = ["TelegramAPI", "Config"]

try:
    from .clients import (
        MultiAccountManager as _MAM,
        get_multi_manager as _gmm,
        create_multi_account_manager as _cmam,
    )
except ModuleNotFoundError as e:
    missing = getattr(e, "name", None)
    if missing not in (
        "telethon",
        f"{__package__}.clients",
        f"{__package__}",
    ):
        raise

    def _telethon_required():
        return (
            "Telethon не установлен. Установите `pip install telethon`"
            "или extras: `pip install kos_Htools[telethon]`."
        )

    class MultiAccountManager:
        """Заглушка: Telethon не установлен."""
        def __init__(self, *args, **kwargs):
            raise RuntimeError(_telethon_required())

    def get_multi_manager(*args, **kwargs):
        """Заглушка: Telethon не установлен."""
        raise RuntimeError(_telethon_required())

    def create_multi_account_manager(*args, **kwargs):
        """Заглушка: Telethon не установлен."""
        raise RuntimeError(_telethon_required())
else:
    MultiAccountManager = _MAM
    get_multi_manager = _gmm
    create_multi_account_manager = _cmam
    __all__ += ["MultiAccountManager", "get_multi_manager", "create_multi_account_manager"]