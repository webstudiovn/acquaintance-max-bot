import logging
import uuid

from yoomoney import Quickpay, AsyncClient

from app.configs.tariffs import TARIFFS
from app.configs.settings import settings

logger = logging.getLogger(__name__)


def create_payment_url(user_id: int, tariff: str) -> tuple[str, str]:
    """
    Создаёт платёжную ссылку YooMoney.
    Возвращает (payment_url, label).
    """
    tariff_info = TARIFFS[tariff]
    price = tariff_info["price"]
    title = tariff_info["title"]

    label = f"user_{user_id}_{tariff}_{uuid.uuid4().hex[:8]}"

    quickpay = Quickpay(
        receiver=settings.yoomoney.receiver,
        quickpay_form="shop",
        targets=f"Оплата {title}",
        paymentType="SB",
        sum=price,
        label=label,
    )

    return quickpay.redirected_url, label


async def check_payment_status(label: str) -> bool:
    """
    Проверяет статус оплаты по label через API YooMoney.
    Возвращает True, если деньги поступили.
    """
    try:
        async with AsyncClient(settings.yoomoney.token) as client:
            history = await client.operation_history(label=label)

            for operation in history.operations:
                if operation.status == "success" and operation.direction == "in":
                    return True
    except Exception as e:
        logger.warning(f"YooMoney API ошибка для label={label}: {e}")
        return False

    return False
