from maxo.utils.builders import KeyboardBuilder

payment_keyboard = (
    KeyboardBuilder()
    .add_callback(text="Условия покупки мэтчей",
                  payload="buying_matches")
).build()