from magic_filter import F
from maxo import Router
from maxo.types import CallbackQuery
from maxo.integrations.magic_filter import MagicFilter
from app.keyboards.tariffs_keyboard import tariffs_keyboard

router = Router()
@router.callback_query(MagicFilter(F.payload.startswith("buying_matches")))
async def payment_handler(callback: CallbackQuery):
    await callback.answer_text(f"Правила пополнение мэтчей:\n"
                               f"Тариф №1 - 160 рублей\n"
                               f"Открывает 5 мэтчей и 1 неделя просмотра анкет.\n\n"
                               f"Тариф №2 - 300 рублей\n"
                               f"Открывает 10 мэтчей и 2 недели просмотра анкет.\n\n"
                               f'Тариф №3 "Супер" 800 рублей\n'
                               f"Безлимитный просмотр мэтчей и анкет в течении месяца",
                               keyboard=tariffs_keyboard)