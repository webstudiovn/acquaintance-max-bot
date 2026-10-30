from magic_filter import F
from maxo.integrations.magic_filter import MagicFilter
import asyncio
from maxo import Router
from maxo.types import CallbackQuery
from sqlalchemy import select
from app.services.notification_service import NotificationService
from app.services.profile_service import ProfileService
from app.database.models.base import async_session_maker
from app.database.models.user import User
from app.handlers.commands.search_pairs import show_profiles_for_user

router = Router()


async def delete_message_after_delay(bot, mid: str, delay: float = 5.0):
    """Удаляет сообщение по mid через задержку."""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(message_id=mid)
    except Exception:
        # Сообщение могло быть удалено ранее или нет прав — тихо игнорируем
        pass


@router.callback_query(MagicFilter(F.payload.startswith("like_") | F.payload.startswith("dislike_")))
async def handle_reaction(callback: CallbackQuery):
    data = callback.data
    if not data or not data.startswith(("like_", "dislike_")):
        return

    parts = data.split("_", 1)
    if len(parts) != 2:
        return

    action, target_id_str = parts
    try:
        target_user_id = int(target_id_str)
    except ValueError:
        return

    liker_user = callback.user
    if not liker_user:
        return
    liker_user_id = liker_user.user_id

    if action == "like":
        result = await NotificationService.send_like_notification(
            callback.bot,
            target_user_id,
            liker_user_id,
        )

        if result:
            msg = await callback.bot.send_message(
                user_id=liker_user_id,
                text="❤️ Вы поставили лайк! Уведомление исчезнет через 5 секунд.",
            )

            mid = msg.message.body.mid
            asyncio.create_task(
                delete_message_after_delay(
                    callback.bot,
                    mid,
                    delay=5.0,
                )
            )
        else:
            await callback.answer_text("⚠️ Не удалось отправить уведомление получателю.")

    elif action == "dislike":
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.max_id == target_user_id)
            )
            profile = result.scalars().first()

            if not profile:
                await callback.answer_text("❌ Анкета не найдена")
                return

            await ProfileService.increment_dislike(session, profile.pk_id)
            await session.commit()

        await callback.answer_text(text="💔 Вы поставили дизлайк. Ищу следующую анкету...")

        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.max_id == liker_user_id)
            )
            current_user = result.scalars().one_or_none()

            if not current_user:
                await callback.bot.send_message(
                    user_id=liker_user_id,
                    text="Ошибка: профиль пользователя не найден.",
                )
                return

            await show_profiles_for_user(callback.message, session, current_user)
