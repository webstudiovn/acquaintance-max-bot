import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.tariffs import TARIFFS
from app.database.models.payment import PaymentOrder, PaymentStatus
from app.database.models.user import User
from app.services.payment.yoomoney_service import create_payment_url, check_payment_status
from app.services.payment.qr_service import generate_qr_code

logger = logging.getLogger(__name__)


async def create_payment_order(
    user_id: int,
    tariff: str,
    session: AsyncSession,
) -> dict:
    """Создаёт платёжную ссылку, QR-код и сохраняет заказ в БД."""
    if tariff not in TARIFFS:
        raise ValueError(f"Неизвестный тариф: {tariff}")

    tariff_info = TARIFFS[tariff]
    price = tariff_info["price"]
    title = tariff_info["title"]

    payment_url, label = create_payment_url(user_id, tariff)
    qr_buffer = generate_qr_code(payment_url)

    # Находим пользователя по max_id
    result = await session.execute(select(User).where(User.max_id == user_id))
    user_obj = result.scalar_one_or_none()

    if not user_obj:
        raise ValueError("Пользователь не найден в БД")

    order = PaymentOrder(
        user_pk_id=user_obj.pk_id,
        tariff=tariff,
        amount=price,
        label=label,
        status=PaymentStatus.pending,
        is_paid=False,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)

    return {
        "payment_url": payment_url,
        "qr_buffer": qr_buffer,
        "label": label,
        "price": price,
        "title": title,
        "order_id": order.id,
    }


async def activate_tariff(
    label: str,
    session: AsyncSession,
) -> bool:
    """
    Проверяет оплату по label и, если она прошла — обновляет заказ и юзера.
    Возвращает True, если тариф активирован (или был активирован ранее).
    """
    result = await session.execute(
        select(PaymentOrder).where(PaymentOrder.label == label)
    )
    order = result.scalar_one_or_none()

    if not order:
        logger.error(f"Заказ с label={label} не найден")
        return False

    if order.is_paid:
        return True

    paid = await check_payment_status(label)

    if not paid:
        return False

    now = datetime.now(timezone.utc)
    tariff_info = TARIFFS[order.tariff]
    matches_to_add = tariff_info["matches"]
    duration_days = tariff_info["duration_days"]

    # Обновляем заказ
    order.status = PaymentStatus.paid
    order.is_paid = True
    order.paid_at = now
    order.expires_at = now + timedelta(days=duration_days)

    # Обновляем юзера
    result = await session.execute(
        select(User).where(User.pk_id == order.user_pk_id)
    )
    user = result.scalar_one_or_none()

    if user:
        if matches_to_add == -1:
            user.matches_count = 999999
        else:
            user.matches_count += matches_to_add

        user.payment_date = now
        user.tariff_type = order.tariff

    await session.commit()

    logger.info(
        f"Тариф активирован: user={user.max_id if user else '?'}, "
        f"tariff={order.tariff}, matches_added={matches_to_add}, "
        f"expires_at={order.expires_at}"
    )
    return True
