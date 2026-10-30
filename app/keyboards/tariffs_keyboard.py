from maxo.utils.builders import KeyboardBuilder

tariffs_keyboard = (
    KeyboardBuilder()
    .add_callback(text="Тариф №1", payload="tariff_one")
    .add_callback(text="Тариф №2", payload="tariff_two")
    .add_callback(text='Тариф №3 "Супер"', payload="tariff_three")
    .add_callback(text="Проверить оплату", payload="check_payment")
).build()