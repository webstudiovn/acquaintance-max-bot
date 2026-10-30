import logging
from typing import Optional

from maxo.types import MessageCreated
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.user import User

logger = logging.getLogger(__name__)


async def show_profiles_for_user(
    msg: MessageCreated,
    session: Session,
    user: User,
    limit: int = 5,
    offset: int = 0,
) -> None:
    """
    Показывает анкеты, подходящие пользователю:
      - не сам пользователь
      - активные
      - без дизлайка
      - по гендерным фильтрам (looking_for / gender)
    """

    # Логируем начало формирования выдачи
    logger.info(
        "Формирование выдачи анкет для user_id=%s, gender=%s, looking_for=%s",
        user.max_id,
        user.gender,
        user.looking_for,
    )

    # Базовые условия: не себя, активные, без дизлайка
    query = (
        select(User)
        .where(User.max_id != user.max_id)
        .where(User.is_activate == True)
        .where(User.dislike == 0)
    )

    # Фильтрация по полу: показываем тех, кто подходит под looking_for пользователя
    # Пример: если user.looking_for == "woman", показываем только женщин (gender == "woman")
    if user.looking_for:
        query = query.where(User.gender == user.looking_for)

    # Пагинация
    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    profiles = result.scalars().all()

    logger.info("Найдено анкет для показа: %d", len(profiles))

    if not profiles:
        await msg.answer(
            "К сожалению, сейчас нет подходящих анкет. Попробуйте позже."
        )
        return

    # Показываем каждую анкету (можно адаптировать под свой формат сообщения)
    for profile in profiles:
        text = (
            f"👤 {profile.name}\n"
            f"📍 {profile.city or 'Город не указан'}\n"
            f"🎂 {profile.age} лет\n"
            f"{profile.about or 'О себе не написано'}\n"
        )

        # Если есть клавиатура с кнопками «Нравится» / «Дизлайк» — используй её
        # keyboard = get_profile_keyboard(profile.max_id)  # раскомментируй, если есть
        # await msg.answer(text, keyboard=keyboard)

        await msg.answer(text)

    # Опционально: если нужно показывать кнопку «Ещё анкеты» после пачки
    if len(profiles) == limit:
        # Можно добавить кнопку «Дальше» и хранить offset в FSM/БД
        await msg.answer("Нажмите /next, чтобы увидеть ещё анкеты.")
