import logging
from typing import Type, Optional, Dict, Any, Tuple
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
        
    async def get_all_column_values(
        self, 
        columns: ColumnElement | Tuple[ColumnElement, ...], 
        where: ColumnElement | None = None
    ) -> list[Any] | list[Tuple[Any, ...]]:
        """
        Получает список всех значений указанных столбца(-ов) для данной модели,
        опционально фильтруя записи по условию.

        columns: Один столбец (ColumnElement) или кортеж столбцов (Tuple[ColumnElement, ...]),
                значения которых нужно получить.
        where: Опциональное условие для фильтрации записей (например, User.user_id == 123456).

        
        Возвращает список значений, где каждый элемент - это значение одного столбца (если был передан один столбец),
            или кортеж значений нескольких столбцов (если был передан кортеж столбцов).
        """
        try:
            stmt = select(*columns) if isinstance(columns, tuple) else select(columns)
            if where is not None:
                stmt = stmt.where(where)
            
            result = await self.db_session.execute(stmt)

            if isinstance(columns, Tuple):
                return result.fetchall()
            else:
                return [row[0] for row in result.fetchall()]
        
        except Exception as e:
            logger.error(f"DAO Ошибка при получении значений колонок: {e}")
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

        attrs_null: Список строк, представляющих имена атрибутов модели,
                    которые нужно обнулить (установить в None).
        where: Условие для поиска записей (например, User.is_active == True).

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

    async def get_one_ordered_or_none(
        self, where: ColumnElement, order_by_clause: ColumnElement | None = None
    ) -> Optional[DeclarativeMeta]:
        """
        Получает один объект модели по условию, используя сортировку для детерминированного выбора,
        если условию соответствует несколько записей (например, при наличии дубликатов в колонке).

        where: Условие для поиска объекта (например, User.user_id == 123456).
        order_by_clause: Опциональный столбец или выражение для сортировки
                        результатов перед выбором первого. Например, User.id.desc().
                        Если не указан, порядок не гарантирован при наличии дубликатов.

        
        Возвращает один объект модели, удовлетворяющий условию и сортировке, или None, если не найдено.
        """
        try:
            stmt = select(self.model).where(where)
            if order_by_clause is not None:
                stmt = stmt.order_by(order_by_clause)
            
            result = await self.db_session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logger.error(f'DAO Ошибка при получении одного объекта с сортировкой: {e}')
            return None


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