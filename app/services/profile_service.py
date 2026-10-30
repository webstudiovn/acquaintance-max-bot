# app/services/profile_service.py
import uuid
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User

class ProfileService:
    @staticmethod
    async def increment_dislike(session: AsyncSession, pk_id: str | uuid.UUID) -> None:
        """Увеличивает dislike на 1 для анкеты"""
        stmt = (
            update(User)
            .where(User.pk_id == pk_id)
            .values(dislike=User.dislike + 1)
        )
        await session.execute(stmt)
        # commit делаем снаружи, чтобы можно было объединить с другими операциями в одной транзакции

    @staticmethod
    async def get_next_profile(
        session: AsyncSession,
        current_pk_id: str | uuid.UUID,
        user_id: int
    ) -> User | None:
        """
        Возвращает следующую анкету, которую можно показать.
        Сейчас это просто «следующая по pk_id».
        Чтобы не показывать уже просмотренные, нужна отдельная таблица истории просмотров.
        """
        stmt = (
            select(User)
            .where(User.pk_id > current_pk_id)
            .order_by(User.pk_id)
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalars().first()
