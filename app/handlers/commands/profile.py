from maxo import Router
from maxo.routing.filters import Command
from maxo.types import MessageCreated, CallbackQuery
from maxo.fsm import FSMContext, StateFilter
from email_validator import validate_email, EmailNotValidError

from sqlalchemy import select

from app.states.profile import Registration
from app.keyboards.gender_keyboard import gender_keyboard
from app.keyboards.looking_keyboard import looking_keyboard
from app.database.requests import update_user
from app.database.models.user import User
from app.database.models.base import async_session_maker

router = Router()

@router.message_created(Command("profile"))
async def edit_profile(msg: MessageCreated, fsm_context: FSMContext) -> None:
    """Начать обновление профиля"""
    await fsm_context.set_state(Registration.name)
    await msg.answer_text(
        "🔄 Обновление профиля\n\n"
        "Введите своё имя:"
    )


@router.message_created(StateFilter(Registration.name))
async def enter_name(msg: MessageCreated, fsm_context: FSMContext) -> None:
    """Обработка имени пользователя"""
    user_id = msg.user_id
    user_name = msg.text.strip()
    
    await update_user(max_id=user_id, name=user_name)
    await fsm_context.set_state(Registration.age)
    
    await msg.answer_text("Введите свой возраст:")


@router.message_created(StateFilter(Registration.age))
async def enter_age(msg: MessageCreated, fsm_context: FSMContext) -> None:
    """Обработка возраста пользователя"""
    user_id = msg.user_id
    age_text = msg.text.strip()
    
    try:
        user_age = int(age_text)
        
        if user_age < 16 or user_age > 100:
            await msg.answer_text("❌ Возраст должен быть от 16 до 100 лет. Попробуйте снова:")
            return
        
        await update_user(max_id=user_id, age=user_age)
        await fsm_context.set_state(Registration.email)
        
        await msg.answer_text("Введите свою электронную почту:")
        
    except ValueError:
        await msg.answer_text("❌ Некорректный возраст. Введите число (например: 25):")


@router.message_created(StateFilter(Registration.email))
async def enter_email(msg: MessageCreated, fsm_context: FSMContext) -> None:
    """Обработка email пользователя"""
    user_id = msg.user_id
    email = msg.text.strip()
    
    try:
        validated_email = validate_email(email, check_deliverability=False)
        user_email = validated_email.email
        
        await update_user(max_id=user_id, email=user_email)
        await fsm_context.set_state(Registration.phone)
        
        await msg.answer_text("Введите свой номер телефона:")
        
    except EmailNotValidError:
        await msg.answer_text("❌ Некорректная электронная почта. Введите правильный email:")


@router.message_created(StateFilter(Registration.phone))
async def enter_phone(msg: MessageCreated, fsm_context: FSMContext) -> None:
    """Обработка телефона пользователя"""
    user_id = msg.user_id
    phone = msg.text.strip()
    
    if len(phone) < 5:
        await msg.answer_text("❌ Слишком короткий номер. Введите правильный номер телефона:")
        return
    
    await update_user(max_id=user_id, phone=phone)
    await fsm_context.set_state(Registration.city)
    
    await msg.answer_text("Введите свой город:")


@router.message_created(StateFilter(Registration.city))
async def enter_city(msg: MessageCreated, fsm_context: FSMContext) -> None:
    """Обработка города пользователя"""
    user_id = msg.user_id
    city = msg.text.strip()
    
    if len(city) < 2:
        await msg.answer_text("❌ Название города слишком короткое. Введите снова:")
        return
    
    await update_user(max_id=user_id, city=city)
    await fsm_context.set_state(Registration.photo_id)
    
    await msg.answer_text("📸 Пришлите Вашу фотографию:")


@router.message_created(StateFilter(Registration.photo_id))
async def enter_photo(msg: MessageCreated, fsm_context: FSMContext) -> None:
    """Обработка фото пользователя"""
    user_id = msg.user_id
    attachments = msg.message.body.attachments
    
    if not attachments:
        await msg.answer_text("❌ Пожалуйста, пришлите фотографию.")
        return

    photo_token = attachments[0].payload.token
    await update_user(max_id=user_id, photo_id=photo_token)
    await fsm_context.set_state(Registration.gender)
    
    await msg.answer_text(
        "Выберите Ваш пол:",
        keyboard=gender_keyboard
    )


@router.callback_query(StateFilter(Registration.gender))
async def select_gender(call: CallbackQuery, fsm_context: FSMContext) -> None:
    """Обработка выбора пола"""
    user_id = call.from_user.user_id
    gender = call.data
    
    await update_user(max_id=user_id, gender=gender)
    await fsm_context.set_state(Registration.looking_for)
    
    await call.message.answer_text(
        "Выберите кого ищете?",
        keyboard=looking_keyboard
    )


@router.callback_query(StateFilter(Registration.looking_for))
async def select_looking_for(call: CallbackQuery, fsm_context: FSMContext) -> None:
    """Обработка выбора кого ищет пользователь"""
    user_id = call.from_user.user_id
    looking_for = call.data
    
    await update_user(max_id=user_id, looking_for=looking_for)
    await fsm_context.set_state(Registration.about)
    await call.message.answer_text("Расскажите немного о себе")


@router.message_created(StateFilter(Registration.about))
async def enter_about(msg: MessageCreated, fsm_context: FSMContext) -> None:
    user_id = msg.user_id
    about = msg.text.strip()

    if len(about) < 2:
        await msg.answer_text("Текст слишком короткий. Напишите хотя бы 2 символа.")
        return
    
    await update_user(max_id=user_id, about=about)
    await fsm_context.set_state(Registration.link)
    await msg.answer_text(
        f"Пришлите Вашу пригласительную ссылку.\n"
        f"Она находится в: [Профиль -> Пригласить друзей]\n"
        f"(Отправьте просто токен, без текста, всё, что идет после u/)\n"
        f"Без:\n"
        f"❌ Http/Https\n"
        f".ru\n"
        f"✅ Всё, что идет после u/"
    )


@router.message_created(StateFilter(Registration.link))
async def enter_link(msg: MessageCreated, fsm_context: FSMContext) -> None:
    user_id = msg.user_id
    link = msg.text.strip()

    await update_user(max_id=user_id, link=link)

    # Получаем пользователя из БД, чтобы показать актуальное matches_count
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.max_id == user_id))
        user = result.scalars().first()

    matches_count = user.matches_count if user else 0

    await fsm_context.clear()
    await msg.answer_text(
        "✅ Ваш профиль успешно обновлён!\n"
        f"Вам предоставляется: {matches_count} мэтчей в подарок\n"
        "Теперь можете выбрать пару: /start"
    )
