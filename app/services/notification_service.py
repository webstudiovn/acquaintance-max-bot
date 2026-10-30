from app.database.models.user import User
from app.database.models.base import async_session_maker
from sqlalchemy import select

class NotificationService:
    @staticmethod
    async def send_like_notification(bot, target_user_id: int, liker_user_id: int) -> bool:
        try:
            async with async_session_maker() as session:
                # Получаем лайкающего
                liker_result = await session.execute(
                    select(User).where(User.max_id == liker_user_id)
                )
                liker_user = liker_result.scalar_one_or_none()

                if not liker_user:
                    return False

                # Получаем целевого пользователя
                target_result = await session.execute(
                    select(User).where(User.max_id == target_user_id)
                )
                target_user = target_result.scalar_one_or_none()

                if not target_user:
                    return False

                link = liker_user.link or ""
                if link:
                    profile_link = f'<a href="https://max.ru/u/{link}">Посмотреть анкету</a>'
                else:
                    profile_link = "Посмотреть анкету (ссылка отсутствует)"

                notification_text = (
                    f"❤️ Вы понравились {liker_user.name or 'пользователю'}!\n"
                    f"{profile_link}"
                )

                # ✅ Используем правильный параметр (text вместо message)
                await bot.send_message(
                    user_id=target_user.max_id,
                    text=notification_text,          # <-- здесь была ошибка
                )
                return True

        except Exception as e:
            return False
