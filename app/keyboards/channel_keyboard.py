from maxo.utils.builders import KeyboardBuilder
from maxo.types import InlineKeyboardAttachmentRequest, InlineKeyboardAttachmentRequestPayload

async def reaction_channel_keyboard(target_user_id: int):
    """Клавиатура реакций совпадении пар."""
    keyboard = (
        KeyboardBuilder()
        .add_callback(
            text="❤️ Нравится",
            payload=f"coincidence_{target_user_id}"
        )
        .add_callback(
            text="💔 Не нравится",
            payload=f"dislike_{target_user_id}"
        )
        .build()  # <-- build() только в конце, после всех кнопок
    )
    
    # Превращаем клавиатуру в attachment по спецификации Maxo
    kb_attachment = InlineKeyboardAttachmentRequest(
        payload=InlineKeyboardAttachmentRequestPayload(buttons=keyboard),
    )
    return kb_attachment
