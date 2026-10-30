from maxo.utils.builders import KeyboardBuilder

gender_keyboard = (
        KeyboardBuilder()
        .add_callback(
            text="Мужчина",
            payload="man",
        )
        .add_callback(text="Женщина",
                      payload="woman")
        .build()
    )