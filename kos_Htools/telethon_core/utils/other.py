import logging

logger = logging.getLogger(__name__)

def format_proxy_string(proxy_str: str) -> tuple | None:
    """
    Преобразует строку прокси в tuple для Telethon
    
    Форматы:
    socks5:ip:port:username:password
    socks5:ip:port
    http:ip:port
    
    Returns:
        tuple: (proxy_type, host, port, username, password) или (proxy_type, host, port)
    """
    if not proxy_str or proxy_str.lower() == 'none':
        return None
    
    parts = proxy_str.split(':')
    if len(parts) < 3:
        logger.error(f'Не правильный формат прокси: {proxy_str}')
        return None
    
    proxy_type = parts[0].lower()
    host = parts[1]
    try:
        port = int(parts[2])
    except ValueError:
        logger.error(f"Порт должен быть числом: {parts[2]}")
        return None
    
    if len(parts) >= 5 and all(isinstance(part, str) for part in [parts[3], parts[4]]):
        username = parts[3]
        password = parts[4]
        return (proxy_type, host, port, username, password)
    else:
        return (proxy_type, host, port)
