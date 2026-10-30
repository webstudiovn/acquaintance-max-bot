from maxo.utils.builders import KeyboardBuilder

async def reaction_keyboard(target_user_id: int):
    """Клавиатура реакций под анкету."""
    keyboard = (
        KeyboardBuilder()
        .add_callback(
            text="❤️ Нравится",
            payload=f"like_{target_user_id}"
        )
        .add_callback(
            text="💔 Не нравится",
            payload=f"dislike_{target_user_id}"
        )
        .build()
    )
    return keyboard