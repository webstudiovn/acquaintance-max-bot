import logging
from sqlalchemy import select
from app.database.models.user import User, Gender, LookingFor

logger = logging.getLogger(__name__)


def get_target_gender(looking_for: LookingFor | None) -> Gender | None:
    if looking_for is None:
        return None

    mapping = {
        LookingFor.man: Gender.man,
        LookingFor.woman: Gender.woman,
    }
    return mapping.get(looking_for)


async def get_profiles_for_user(session, current_user_id: int, offset: int = 0, limit: int = 5):
    query = select(User).where(User.max_id != current_user_id)

    # Здесь можно позже вынести логику фильтрации в отдельный сервис, если станет сложнее
    # Но пока оставляем в том же стиле, что и у тебя
    target_gender = get_target_gender(None)  # заглушка: передадим looking_for снаружи
    return query.offset(offset).limit(limit)


async def fetch_profiles(session, current_user_id: int, looking_for: LookingFor | None, offset: int = 0, limit: int = 5):
    target_gender = get_target_gender(looking_for)

    query = select(User).where(User.max_id != current_user_id)
    if target_gender is not None:
        logger.info("Применяем фильтр по полу: %r", target_gender.value)
        query = query.where(User.gender == target_gender)
    else:
        logger.warning("looking_for не задан — показываем анкеты без фильтра по полу")

    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()
