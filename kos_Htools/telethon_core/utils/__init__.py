"""
kos_Htools.telethon_core.utils - Утилиты для работы с Telegram
"""
__all__ = []

try:
    from .parse import UserParse as _UserParse
except ModuleNotFoundError as e:
    missing = getattr(e, "name", None)
    if missing not in (
        "telethon",
        f"{__package__}.parse",
        f"{__package__}",
    ):
        raise

    def _telethon_required():
        return (
            "Telethon не установлен. Установите `pip install telethon`"
            "или extras: `pip install kos_Htools[telethon]`."
        )

    def UserParse(*args, **kwargs):
        """Заглушка: Telethon не установлен."""
        raise RuntimeError(_telethon_required())
else:
    UserParse = _UserParse
    __all__ += ["UserParse"]

