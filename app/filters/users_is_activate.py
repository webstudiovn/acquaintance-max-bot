from typing import Optional
from maxo.types import MessageCreated
from app.database.models.user import User
from app.database.models.base import async_session_maker
from sqlalchemy import select


async def filter_inactive_users(msg: MessageCreated) -> Optional[User]:
    """
    Фильтр:
      - проверяет, что пользователь есть в БД;
      - если matches_count == 0 — поиск закрыт, возвращаем None;
      - если matches_count > 0 — возвращаем объект User.
    """
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.max_id == msg.message.sender.user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return None

        # Если лимит мэтчей исчерпан (0) — закрываем поиск
        if user.matches_count <= 0:
            await msg.answer("Лимит совпадений исчерпан. Поиск временно закрыт.")
            return None

        return user
