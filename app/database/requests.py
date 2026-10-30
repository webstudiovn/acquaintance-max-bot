from typing import Optional, Dict, Any
from sqlalchemy import insert, update, select
from app.database.models.base import engine
from app.database.models.user import User

async def get_user_by_id(max_id: int) -> Optional[User]:
    """Получить пользователя по ID"""
    async with engine.begin() as conn:
        stmt = select(User).where(User.max_id == max_id)
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

async def insert_user(max_id: int) -> bool:
    """
    Добавляет пользователя, если его нет.
    Возвращает True если добавлен, False если уже существует
    """
    # Сначала проверяем, существует ли пользователь
    existing_user = await get_user_by_id(max_id)
    
    if existing_user:
        return False  # Пользователь уже существует
    
    # Если пользователя нет - добавляем
    async with engine.begin() as conn:
        stmt = insert(User).values(max_id=max_id)
        await conn.execute(stmt)
        return True  # Пользователь успешно добавлен

async def update_user(
    max_id: int,
    photo_id: Optional[int] = None,
    name: Optional[str] = None,
    gender: Optional[str] = None,
    looking_for: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    city: Optional[str] = None,
    age: Optional[int] = None,
    about: Optional[str] = None,
    link: Optional[str] = None
) -> bool:
    """
    Обновляет данные пользователя.
    Возвращает True если обновление выполнено, False если пользователь не найден
    """
    # Проверяем существование пользователя
    existing_user = await get_user_by_id(max_id)
    if not existing_user:
        return False  # Пользователь не найден
    
    # Собираем данные в словарь
    data: Dict[str, Any] = {}

    # Заполняем только те поля, которые явно переданы (не None)
    if photo_id is not None:
        data["photo_id"] = photo_id
    if name is not None:
        data["name"] = name
    if gender is not None:
        data["gender"] = gender
    if looking_for is not None:
        data["looking_for"] = looking_for
    if phone is not None:
        data["phone"] = phone
    if email is not None:
        data["email"] = email
    if city is not None:
        data["city"] = city
    if age is not None:
        data["age"] = age
    if about is not None:
        data["about"] = about
    if link is not None:
        data["link"] = link

    # Если data пустой — обновлять нечего
    if not data:
        return True  # Все хорошо, но ничего не обновлено

    async with engine.begin() as conn:
        stmt = (
            update(User)
            .where(User.max_id == max_id)
            .values(**data)
        )
        await conn.execute(stmt)
        return True  # Обновление выполнено успешно