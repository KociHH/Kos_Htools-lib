import logging
import random
from typing import Dict, List, Optional, Union
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import ChannelParticipantsSearch, Channel, PeerChannel, User
from telethon.errors import UserAlreadyParticipantError
import asyncio


logger = logging.getLogger(__name__)

class UserParse:
    def __init__(self, client: TelegramClient, chat_usernames: dict[str, list], chat_id: Optional[int] = None):
        self.client = client
        self.chat_usernames = chat_usernames
        self.chat_id = chat_id
        self.user_ids = {} # {chat_id | username: [int]}
        self.user_messages = {} # {user_id: {chat_name: message_count, total_message: int}}
        
    def __call__(self) -> bool:
        if not ('chats' in self.chat_usernames or 'channles' in self.chat_usernames):
            logger.warning(
                'В вашем словаре нет ключей chats и channles\n'
                'Словарь должен выглядеть так:\n\n'
                '{chats: [user | link] или channels: [link]}'
            )
            return False
        return True


    async def check_and_switch_client(self) -> bool:
        """
        Проверяет количество чатов и при необходимости меняет клиента
        
        Returns:
            bool: True если проверка прошла успешно, False если есть проблемы
        """
        from ...telethon_core import multi
        
        total_chats = len(self.chat_usernames.get('chats', [])) + len(self.chat_usernames.get('channles', []))
        
        if total_chats > 100:
            available_clients = len(multi.clients)
            
            if available_clients <= 1:
                logger.warning(
                    'Опасно! Слишком много чатов для одного клиента.\n'
                    f'Всего чатов: {total_chats}\n'
                    'Рекомендуется добавить больше клиентов или уменьшить количество чатов.'
                )
                return False
            
            new_client = await multi.get_or_switch_client(switch=True)
            if not new_client:
                logger.error('Не удалось сменить клиента')
                return False
                
            self.client = new_client
            logger.info(f'Клиент успешно изменен. Новый клиент: {self.client}')
            
            if 'chats' in self.chat_usernames:
                valid_chats = []
                for chat in self.chat_usernames['chats']:
                    try:
                        entity = await self.client.get_entity(chat)
                        if await self.client.is_user_authorized() and await self.client.get_participants(entity, limit=1):
                            valid_chats.append(chat)
                            if len(valid_chats) >= 100:
                                break
                    except Exception:
                        continue
                
                self.chat_usernames['chats'] = valid_chats
                logger.info(f'Оставлено {len(valid_chats)} валидных чатов')
        
        return True


    async def check_account(self, user_id: Union[str, int]) -> bool:
        """    
        Проверяет, не удален ли аккаунт пользователя
        
        Args:
            user_id: ID пользователя для проверки
            
        Returns:
            bool: True если аккаунт активен, False если удален
        """
        try:
            entity = await self.client.get_entity(user_id)
            if isinstance(entity, User):
                if entity.deleted:
                    logger.info(f'Аккаунт {user_id} удален, пропускаем')
                    return False
                
                if entity.bot:
                    logger.info(f'Аккаунт {user_id} - это бот, пропускаем')
                    return False
                
                if entity.restricted:
                    logger.info(f'Аккаунт {user_id} ограничен, пропускаем')
                    return False
                
                return True
            return False
            
        except Exception as e:
            logger.warning(f'Ошибка при проверке аккаунта {user_id}: {e}')
            return False


    async def get_linked_chat(self, channel: Union[str, int]) -> Optional[int]:
        """
        Получает ID привязанной группы для канала
        
        Args:
            channel: username или ID канала
            
        Returns:
            Optional[int]: ID привязанной группы или None, если её нет
        """
        try:
            entity = await self.client.get_entity(channel)
            if isinstance(entity, Channel):
                full = await self.client(GetFullChannelRequest(channel=entity))
                return full.full_chat.linked_chat_id
        except Exception as e:
            logger.error(f'Ошибка при получении привязанной группы для канала {channel}:\n {e}')
        return None


    async def collect_user_ids(self, check_delete_acc: bool = True) -> dict[Union[int, str], list[int]]:
        """
        Return:
            dict[str: [int]] -> {chat_id | username: [int]}
        """
        try:
            if not await self.check_and_switch_client():
                return {}
            
            if 'chats' in self.chat_usernames:
                for chat in self.chat_usernames['chats']:
                    logger.info(f'Текущий чат: {chat}')
                    if self.user_ids:
                        timer = random.randint(5, 10)
                        logger.info(f'Ждем {timer} секунд..')
                        asyncio.sleep(timer)
                    try:
                        entity = await self.client.get_entity(chat)
                        self.user_ids[chat] = []
                        async for user in self.client.iter_participants(entity):
                            if check_delete_acc:
                                if not await self.check_account(user.id):
                                    continue
                            self.user_ids[chat].append(user.id)
                            
                        logger.info(
                            f'Успешный парсинг чата {chat}\n'
                            f'Кол-во user_id собрано в чате: {len(self.user_ids[chat])}'
                        )
                    except Exception as e:
                        logger.warning(f'Ошибка при обработке {chat}:\n {e}')
                
                logger.info(
                    'Успешно спарсены чаты:\n' + 
                    '\n'.join(f'- {chat}' for chat in self.chat_usernames['chats'])
                )
            
            if 'channles' in self.chat_usernames:
                for channel in self.chat_usernames['channles']:           
                    try:
                        linked_id = await self.get_linked_chat(channel)
                        
                        if linked_id:
                            linked_chat = await self.client.get_entity(linked_id)
                            logger.info(f'Найдена привязанная группа для канала {channel}: {linked_id}')
                            
                            self.user_ids[channel] = []
                            async for user in self.client.iter_participants(linked_chat):
                                if check_delete_acc:
                                    if not await self.check_account(user.id):
                                        continue
                                self.user_ids[channel].append(user.id)
                            
                            logger.info(
                                f"Привязанная группа канала {channel} успешно спарсена.\n"
                                f'Кол-во user_id: {len(self.user_ids[channel])}'
                            )
                        else:
                            logger.warning(f'У канала {channel} нет привязанной группы. Пропускаем...')
                    
                    except Exception as e:
                        logger.error(f'Ошибка при парсинге канала {channel}:\n {e}')
                    
        except Exception as e:
            logger.error(f'Ошибка при парсе user_id в функции collect_user_ids:\n {e}')
        return self.user_ids if self.user_ids else logger.debug('id с чатов был спарсен но не добавлен на выход')
    

    async def collect_user_messages(self, limit: int | None = 100, sum_count: bool = False) -> Dict[int, Dict[str, int]]:
        """
        Args:
            limit (int): Максимальное количество сообщений для анализа в каждом чате
            sum_count: Вычисляет кол-во сообщение во всех чатах
            
        Returns:
            Dict[int, Dict[str, int]] -> {user_id: {chat_name: message_count, total_message: int}}
        """
        try:
            all_chats = []
            if 'chats' in self.chat_usernames:
                all_chats.extend(self.chat_usernames['chats'])
            if 'channles' in self.chat_usernames:
                all_chats.extend(self.chat_usernames['channles'])
            
            if not self.check_and_switch_client():
                return {}

            for chat in all_chats:
                try:
                    if chat in self.chat_usernames.get('channles', []):
                        linked_id = await self.get_linked_chat(chat)
                        if linked_id:
                            chat = linked_id
                            logger.info(f'Используем привязанную группу {linked_id} вместо канала {chat}')
                    
                    entity = await self.client.get_entity(chat)
                    chat_name = getattr(entity, 'title', str(chat))
                    
                    # main collection
                    async for message in self.client.iter_messages(entity, limit=limit):
                        if message.from_id and hasattr(message.from_id, 'user_id'):
                            user_id = message.from_id.user_id
                            if await self.check_account(user_id):
                                if user_id not in self.user_messages:
                                    self.user_messages[user_id] = {}
                            
                                if chat_name not in self.user_messages[user_id]:
                                    self.user_messages[user_id][chat_name] = 0
                                self.user_messages[user_id][chat_name] += 1
                            
                except Exception as e:
                    logger.error(f'Ошибка при подсчете сообщений в чате {chat}:\n {e}')
            
            if sum_count:
                for user_id in self.user_messages:
                    total_messages = sum(self.user_messages[user_id].values())
                    self.user_messages[user_id]['total_messages'] = total_messages
            
            return self.user_messages if self.user_messages else \
                   logger.debug('Пустой список, парсинг был произведен но данные не найдены или их НЕТ')
            
        except Exception as e:
            logger.error(f'Ошибка при подсчете сообщений пользователей:\n {e}')
            return {}