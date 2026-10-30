# app/services/user_service.py
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.user import User
import logging

logger = logging.getLogger(__name__)

async def get_active_user(session: Session, user_id: int) -> Optional[User]:
    """
    Возвращает пользователя только если он существует и активен.
    Если неактивен — логирует и возвращает None.
    """
    result = await session.execute(
        select(User).where(User.max_id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Пользователь %s не найден в БД", user_id)
        return None

    if not user.is_activate:
        logger.info("Доступ запрещён: пользователь %s неактивен", user.max_id)
        return None

    return user
