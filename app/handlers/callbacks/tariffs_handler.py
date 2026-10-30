# app/handlers/callbacks/tariffs_handler.py

import asyncio
import logging
from maxo import Router
from magic_filter import F
from maxo.types import CallbackQuery
from maxo.integrations.magic_filter import MagicFilter
from maxo.utils.upload_media import BufferedInputFile
from sqlalchemy import select
from app.database.models.payment import PaymentOrder, PaymentStatus
from app.database.models.user import User

from app.services.payment import (
    create_payment_order,
    wait_for_payment_and_activate,
    activate_tariff,
)
from app.database.models.base import async_session_maker

router = Router()
logger = logging.getLogger(__name__)


async def _process_tariff(callback: CallbackQuery, tariff: str):
    user_id = callback.from_user.id

    try:
        async with async_session_maker() as session:
            order = await create_payment_order(user_id, tariff, session)

        caption = (
            f"{order['title']} — {order['price']} ₽\n\n"
            f"Отсканируйте QR-код камерой телефона или "
            f"перейдите по ссылке для оплаты.\n"
            f"После оплаты доступ активируется автоматически.\n\n"
            f"Ссылка на оплату:\n{order['payment_url']}"
        )

        photo = BufferedInputFile.image(
            order["qr_buffer"].getvalue(),
            "qr_payment.png",
        )

        await callback.send_media(
            media=photo,
            text=caption,
        )

        logger.info(
            f"Заказ #{order['order_id']} создан: "
            f"user={user_id}, tariff={tariff}, label={order['label']}"
        )

        asyncio.create_task(
            wait_for_payment_and_activate(
                label=order["label"],
                bot=callback.bot,
                user_id=user_id,
                timeout=600,
                interval=15,
            )
        )

    except Exception as e:
        logger.error(f"Ошибка создания заказа: {e}", exc_info=True)
        await callback.answer_text(
            "Произошла ошибка при создании заказа. Попробуйте позже."
        )


@router.callback_query(MagicFilter(F.data == "tariff_one"))
async def tariff_one_handler(callback: CallbackQuery):
    await _process_tariff(callback, "tariff_one")


@router.callback_query(MagicFilter(F.data == "tariff_two"))
async def tariff_two_handler(callback: CallbackQuery):
    await _process_tariff(callback, "tariff_two")


@router.callback_query(MagicFilter(F.data == "tariff_three"))
async def tariff_three_handler(callback: CallbackQuery):
    await _process_tariff(callback, "tariff_three")


@router.callback_query(MagicFilter(F.data == "check_payment"))
async def check_payment_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    await callback.answer_text("Проверяю оплату...")

    try:
        async with async_session_maker() as session:
            user_result = await session.execute(
                select(User).where(User.max_id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                logger.info(f"check_payment: пользователь {user_id} не найден в БД")
                await callback.answer_text("Пользователь не найден.")
                return

            order_result = await session.execute(
                select(PaymentOrder)
                .where(
                    PaymentOrder.user_pk_id == user.pk_id,
                    PaymentOrder.status == PaymentStatus.pending,
                )
                .order_by(PaymentOrder.created_at.desc())
                .limit(1)
            )
            order = order_result.scalar_one_or_none()

            if not order:
                logger.info(f"check_payment: pending-заказов для user {user_id} нет")
                await callback.answer_text("У вас нет ожидающих оплаты заказов.")
                return

            activated = await activate_tariff(order.label, session)

            if activated:
                logger.info(f"check_payment: оплата подтверждена для user {user_id}, label={order.label}")
                await callback.answer_text("✅ Оплата прошла успешно! Мэтчи зачислены.")
            else:
                logger.info(f"check_payment: оплата не найдена для user {user_id}, label={order.label}")
                await callback.answer_text("❌ Оплата ещё не поступила. Попробуйте позже.")

    except Exception as e:
        logger.error(f"Ошибка при ручной проверке оплаты: {e}", exc_info=True)
        await callback.answer_text("Ошибка при проверке оплаты. Попробуйте позже.")
