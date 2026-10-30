# app/handlers/callbacks/matches_handler.py

import logging
from magic_filter import F
from maxo import Router
from maxo.types import CallbackQuery
from maxo.integrations.magic_filter import MagicFilter
from sqlalchemy import select, or_, and_

from app.database.models.base import async_session_maker
from app.database.models.match_user import Match
from app.database.models.user import User

logging.basicConfig(level=logging.INFO)

router = Router()


@router.message_callback(MagicFilter(F.payload.startswith("coincidence_")))
async def matches_reaction(callback: CallbackQuery):
    data = callback.data
    if not data or not data.startswith("coincidence_"):
        return

    logging.info(f"Coincidence callback received: {data}")

    parts = data.split("_", 1)
    if len(parts) != 2:
        return

    _, target_id_str = parts
    try:
        target_user_id = int(target_id_str)
    except ValueError:
        return

    liker = callback.user
    if not liker:
        return
    liker_user_id = liker.user_id

    if liker_user_id == target_user_id:
        await callback.answer_text("⚠️ Нельзя поставить совпадение самому себе")
        return

    # Нормализуем пару: меньший ID → user_id_1, больший → user_id_2
    user_id_1 = min(liker_user_id, target_user_id)
    user_id_2 = max(liker_user_id, target_user_id)

    async with async_session_maker() as session:
        # --- Получаем текущего пользователя, чтобы проверить и уменьшить matches_count ---
        liker_result = await session.execute(
            select(User).where(User.max_id == liker_user_id)
        )
        liker_user = liker_result.scalars().first()

        if liker_user is None:
            return

        # Если мэтчи уже закончились — не даём поставить новый
        if liker_user.matches_count <= 0:
            await callback.answer_text("Лимит совпадений исчерпан. Поиск временно закрыт.")
            return

        # Отнимаем один мэтч
        liker_user.matches_count -= 1
        remaining = liker_user.matches_count

        # Ищем существующую запись о паре
        result = await session.execute(
            select(Match).where(
                or_(
                    and_(
                        Match.user_id_1 == user_id_1,
                        Match.user_id_2 == user_id_2,
                    ),
                    and_(
                        Match.user_id_1 == user_id_2,
                        Match.user_id_2 == user_id_1,
                    ),
                )
            )
        )
        match = result.scalars().first()

        if match is None:
            # Создаём новую запись
            match = Match(
                user_id_1=user_id_1,
                user_id_2=user_id_2,
            )
            session.add(match)

        # Ставим флаг в зависимости от того, кто лайкнул
        if liker_user_id == user_id_1:
            match.has_match_1_to_2 = True
        else:
            match.has_match_2_to_1 = True

        await session.flush()

        both_liked = match.has_match_1_to_2 and match.has_match_2_to_1

        if both_liked and not match.notification_sent:
            # Достаём анкеты обоих пользователей для имён
            user1_result = await session.execute(
                select(User).where(User.max_id == user_id_1)
            )
            user1 = user1_result.scalars().first()

            user2_result = await session.execute(
                select(User).where(User.max_id == user_id_2)
            )
            user2 = user2_result.scalars().first()

            name_1 = user1.name if user1 else "Пользователь"
            name_2 = user2.name if user2 else "Пользователь"

            # Отправляем уведомления обоим
            try:
                await callback.bot.send_message(
                    user_id=user_id_1,
                    text=f"💘 У вас совпадение с {name_2}! Вы понравились друг другу.",
                )
            except Exception as e:
                logging.error(f"Не удалось отправить уведомление user_id_1={user_id_1}: {e}")

            try:
                await callback.bot.send_message(
                    user_id=user_id_2,
                    text=f"💘 У вас совпадение с {name_1}! Вы понравились друг другу.",
                )
            except Exception as e:
                logging.error(f"Не удалось отправить уведомление user_id_2={user_id_2}: {e}")

            match.notification_sent = True

        await session.commit()

    # --- Ответы пользователю ---
    if remaining == 0:
        await callback.answer_text(
            "✅ Ваша симпатия зафиксирована.\n"
            "Лимит совпадений исчерпан. Поиск временно закрыт."
        )
    elif both_liked:
        await callback.answer_text(
            f"💘 Совпадение! Уведомление отправлено вам обоим.\n"
            f"Осталось мэтчей: {remaining}"
        )
    else:
        await callback.answer_text(
            f"✅ Ваша симпатия зафиксирована. Ждём ответа.\n"
            f"Осталось мэтчей: {remaining}"
        )
