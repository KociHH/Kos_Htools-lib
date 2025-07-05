import logging
from typing import Type, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.expression import select, delete, update

logger = logging.getLogger(__name__)

class BaseDAO:
    def __init__(self, model: Type[DeclarativeMeta], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get_one(self, where: ColumnElement) -> Optional[DeclarativeMeta]:
        """
        Получить одну запись модели, удовлетворяющую условию where.
        
        where:
            Условие для обновления записей (User.id == 1).

        Возвращает объект модели или None, если не найдено.
        """
        try:
            result = await self.db_session.execute(select(self.model).where(where))
            return result.scalars().one_or_none()
        except Exception as e:
            logger.error(f'DAO Ошибка: {e}')
            return None

    async def create(self, data: Dict[str, Any]) -> Optional[DeclarativeMeta]:
        """
        Создать новую запись в базе данных на основе словаря data.
        
        data:
            Атрибуты и их значение ("ready": True)
        
        Возвращает созданный объект или None при ошибке.
        """
        try:
            obj = self.model(**data)
            self.db_session.add(obj)
            await self.db_session.commit()
            return obj
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f'DAO Ошибка: {e}')
            return None

    async def update(self, where: ColumnElement, data: Dict[str, Any]) -> bool:
        """
        Обновить запись, найденную по условию where, данными из data.

        where:
            Условие для обновления записей (User.id == 1).
        data:
            Атрибты и их новое значение ("ready": True)
            
        Возвращает True при успехе, иначе False.
        """
        exiting = await self.get_one(where)
        if not exiting:
            logger.warning(f'DAO Объект не найден для обновления по: {where}')
            return False
                
        try:
            update = Update_date(
                base=exiting,
                params=data
            )
            await update.save_(self.db_session)
            return True
        
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f'DAO Ошибка: {e}')
            return False
        
    async def get_all_column_values(self, column) -> list[Any]:
        """
        Получить все значения указанного столбца column для данной модели.
        Возвращает список значений.
        """
        try:
            stmt = select(column)
            result = await self.db_session.execute(stmt)
            return [row[0] for row in result.fetchall()]
        
        except Exception as e:
            logger.error(f"DAO Ошибка при получении значений колонки: {e}")
            return []
        
    async def get_all(self) -> list[DeclarativeMeta]:
        """
        Получить все записи данной модели из базы данных.
        Возвращает список объектов модели.
        """
        try:
            result = await self.db_session.execute(select(self.model))
            return result.scalars().all()
        except Exception as e:
            logger.error(f'DAO Ошибка при получении всех объектов: {e}')
            return []
        
    async def delete(self, where: ColumnElement) -> bool:
        """
        Удаляет записи из базы данных, удовлетворяющие условию.

        where:
            Условие для удаления записей (User.id == 1).

        Возвращает True, если удаление прошло успешно, иначе False.
        """
        try:
            stmt = delete(self.model).where(where)
            await self.db_session.execute(stmt)
            await self.db_session.commit()
            return True
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f'DAO Ошибка при удалении: {e}')
            return False

    async def null_objects(self, attrs_null: list[str], where: ColumnElement) -> bool:
        """
        Обнуляет значения заданных атрибутов (устанавливает в None) во ВСЕХ записях модели,
        удовлетворяющих условию 'where'.

        attrs_null:
            Список строк, представляющих имена атрибутов модели, которые нужно установить в None.
        where: 
            Условие для поиска записей (например, User.is_active == True).

        Возвращает True, если обнуление прошло успешно, иначе False.
        """
        try:
            update_data = {attr_name: None for attr_name in attrs_null}
            stmt = update(self.model).where(where).values(**update_data)
            result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"DAO Ошибка при обнулении элементов: {e}")
            return False

class Update_date:
    def __init__(self, base, params: dict[str, Any]):
        self.base = base
        self.params = params
        self.changes = {}
    
    def update(self) -> dict[str, tuple[str | int]]:
        try:
            for key, items in self.params.items():
                if hasattr(self.base, key):
                    old = getattr(self.base, key)
                    if old != items:
                        setattr(self.base, key, items)
                        self.changes[key] = [old, items]
                else:
                    logger.error(f"Не найден атрибут '{key}' в объекте {self.base.__class__.__name__}")
            return self.changes
            
        except Exception as e:
            logger.error(
                f'Ошибка в классе: {__class__.__name__} в функции update\n'
                f'Причина:\n {e}'
                )
            raise
    
    async def save_(self, db_session: AsyncSession) -> bool:
        try:
            changes = self.update()
            if not changes:
                return True

            db_session.add(self.base)
            await db_session.commit()
            return True
            
        except Exception as e:
            logger.error(f'Ошибка при сохранении в бд: {e}')
            await db_session.rollback()
            return False