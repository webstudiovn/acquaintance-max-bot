import asyncio
import logging

from app.configs.tariffs import TARIFFS
from app.services.payment.order_service import activate_tariff

logger = logging.getLogger(__name__)


async def wait_for_payment_and_activate(
    label: str,
    bot=None,
    user_id: int = None,
    timeout: int = 600,
    interval: int = 15,
):
    """
    Фоновая задача: опрашивает YooMoney каждые `interval` секунд.
    При успехе — активирует тариф и отправляет сообщение юзеру.
    """
    from app.database.models.base import async_session_maker

    elapsed = 0
    while elapsed < timeout:
        await asyncio.sleep(interval)
        elapsed += interval

        try:
            async with async_session_maker() as session:
                activated = await activate_tariff(label, session)

            if activated:
                if bot and user_id:
                    tariff_info = TARIFFS.get(
                        label.split("_")[2] if len(label.split("_")) > 3 else "",
                        {},
                    )
                    matches = tariff_info.get("matches", 0)
                    matches_text = "безлимит" if matches == -1 else str(matches)

                    await bot.send_message(
                        chat_id=user_id,
                        text=(
                            "✅ Оплата прошла успешно!\n\n"
                            f"Вам начислено: {matches_text} мэтчей\n"
                            "Приятного пользования!"
                        ),
                    )
                return

        except Exception as e:
            logger.error(f"Ошибка при проверке оплаты {label}: {e}")

    if bot and user_id:
        await bot.send_message(
            chat_id=user_id,
            text="⏰ Время ожидания оплаты истекло.\nЕсли вы оплатили — нажмите «Проверить оплату».",
        )
