"""
Onboarding FSM Module
Handles user onboarding flow with style adaptation.
"""

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from utils.logger import logger
from utils.style_detector import StyleDetector
from data.storage import Storage


# Initialize dependencies
style_detector = StyleDetector()
storage = Storage()

# Create router for onboarding handlers
onboarding_router = Router()


class OnboardingStates(StatesGroup):
    """FSM states for user onboarding."""
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_goals = State()
    waiting_for_language = State()


class OnboardingQuestions:
    """
    Generates onboarding questions adapted to user's communication style.
    """

    @staticmethod
    def get_welcome_message(style: dict) -> str:
        """Get welcome message for onboarding start."""
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')

        messages = {
            ('formal', 'russian'): (
                "Давайте познакомимся! Я задам вам несколько вопросов, чтобы создать "
                "персональный план развития.\n\n"
                "Вы можете отменить процесс в любой момент командой /cancel"
            ),
            ('casual', 'russian'): (
                "Давай познакомимся! Задам тебе несколько вопросов, чтобы создать "
                "твой персональный план.\n\n"
                "Можешь отменить в любой момент командой /cancel"
            ),
            ('formal', 'kazakh'): (
                "Танысайық! Сізге жеке даму жоспарын құру үшін бірнеше сұрақ қоямын.\n\n"
                "Кез келген уақытта /cancel командасымен тоқтата аласыз"
            ),
            ('casual', 'kazakh'): (
                "Танысайық! Саған жеке жоспар жасау үшін бірнеше сұрақ қояйын.\n\n"
                "/cancel командасымен тоқтата аласың"
            ),
        }

        key = (formality, language)
        return messages.get(key, messages[('casual', 'russian')])

    @staticmethod
    def get_name_question(style: dict) -> str:
        """Get question for name input."""
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')

        messages = {
            ('formal', 'russian'): "Как вас зовут?",
            ('casual', 'russian'): "Как тебя зовут?",
            ('formal', 'kazakh'): "Сіздің атыңыз кім?",
            ('casual', 'kazakh'): "Атың кім?",
        }

        key = (formality, language)
        return messages.get(key, messages[('casual', 'russian')])

    @staticmethod
    def get_age_question(style: dict, name: str) -> str:
        """Get question for age input."""
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')

        messages = {
            ('formal', 'russian'): f"Приятно познакомиться, {name}! Сколько вам лет?",
            ('casual', 'russian'): f"Приятно, {name}! Сколько тебе лет?",
            ('formal', 'kazakh'): f"Танысқаныма қуаныштымын, {name}! Сіз неше жастасыз?",
            ('casual', 'kazakh'): f"Қуаныштымын, {name}! Неше жасың?",
        }

        key = (formality, language)
        return messages.get(key, messages[('casual', 'russian')])

    @staticmethod
    def get_goals_question(style: dict) -> str:
        """Get question for goals input."""
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')

        messages = {
            ('formal', 'russian'): (
                "Расскажите о своих целях и мечтах. Чего вы хотите достичь в ближайшие 5 лет?\n"
                "(Например: карьерный рост, освоение новой профессии, развитие навыков)"
            ),
            ('casual', 'russian'): (
                "Расскажи о своих целях и мечтах. Чего хочешь достичь за 5 лет?\n"
                "(Например: карьера, новая профессия, развитие навыков)"
            ),
            ('formal', 'kazakh'): (
                "Мақсаттарыңыз бен арман-тілектеріңіз туралы айтып беріңізші. "
                "Келесі 5 жылда неге қол жеткізгіңіз келеді?\n"
                "(Мысалы: мансаптық өсу, жаңа мамандықты меңгеру, дағдыларды дамыту)"
            ),
            ('casual', 'kazakh'): (
                "Мақсаттарың мен арман-тілектерің туралы айтып бер. "
                "5 жылда неге жеткің келеді?\n"
                "(Мысалы: мансап, жаңа мамандық, дағдыларды дамыту)"
            ),
        }

        key = (formality, language)
        return messages.get(key, messages[('casual', 'russian')])

    @staticmethod
    def get_language_question(style: dict) -> str:
        """Get question for preferred communication language."""
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')

        messages = {
            ('formal', 'russian'): (
                "На каком языке вам удобнее общаться?\n"
                "Напишите: 'русский' или 'казахский'"
            ),
            ('casual', 'russian'): (
                "На каком языке тебе удобнее?\n"
                "Напиши: 'русский' или 'казахский'"
            ),
            ('formal', 'kazakh'): (
                "Қай тілде сөйлесу ыңғайлы?\n"
                "'орыс' немесе 'қазақ' деп жазыңыз"
            ),
            ('casual', 'kazakh'): (
                "Қай тілде ыңғайлы?\n"
                "'орыс' немесе 'қазақ' деп жаз"
            ),
        }

        key = (formality, language)
        return messages.get(key, messages[('casual', 'russian')])

    @staticmethod
    def get_completion_message(style: dict, name: str) -> str:
        """Get completion message after onboarding."""
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')
        emoji = "✅" if style.get('emoji_usage') == 'high' else ""

        messages = {
            ('formal', 'russian'): (
                f"{emoji} Отлично, {name}! Ваш профиль сохранён.\n\n"
                "Теперь я могу создать для вас персональный план развития. "
                "Используйте /plan когда будете готовы.\n\n"
                "Команды:\n/profile - просмотр профиля\n/plan - создать план"
            ),
            ('casual', 'russian'): (
                f"{emoji} Супер, {name}! Твой профиль сохранён.\n\n"
                "Теперь могу создать для тебя план развития. "
                "Жми /plan когда будешь готов.\n\n"
                "Команды:\n/profile - твой профиль\n/plan - создать план"
            ),
            ('formal', 'kazakh'): (
                f"{emoji} Керемет, {name}! Сіздің профиліңіз сақталды.\n\n"
                "Енді сізге жеке даму жоспарын құра аламын. "
                "Дайын болғанда /plan пайдаланыңыз.\n\n"
                "Командалар:\n/profile - профильді көру\n/plan - жоспар құру"
            ),
            ('casual', 'kazakh'): (
                f"{emoji} Супер, {name}! Профиліңіз сақталды.\n\n"
                "Енді саған даму жоспарын жасай аламын. "
                "Дайын болғанда /plan бас.\n\n"
                "Командалар:\n/profile - профиліңіз\n/plan - жоспар құру"
            ),
        }

        key = (formality, language)
        return messages.get(key, messages[('casual', 'russian')])


@onboarding_router.message(Command("onboarding"))
async def start_onboarding(message: Message, state: FSMContext):
    """
    Start or restart user onboarding process.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "User"

    logger.info(f"User {user_id} (@{username}) started onboarding")

    # Check if user already has a profile
    user_data = storage.load_user_data(user_id)

    if user_data and user_data.get('onboarding_completed'):
        # User already has profile, ask if they want to update
        await message.reply(
            "У вас уже есть профиль. Хотите обновить его?\n"
            "Введите 'да' для обновления или /cancel для отмены."
        )
        # Wait for confirmation in the same state
        await state.set_state(OnboardingStates.waiting_for_name)
        await state.update_data(awaiting_confirmation=True)
        return

    # Detect initial style from any previous messages
    initial_style = style_detector.analyze_style(message.text or "")

    # Send welcome message
    welcome = OnboardingQuestions.get_welcome_message(initial_style)
    await message.reply(welcome)

    # Ask first question
    name_question = OnboardingQuestions.get_name_question(initial_style)
    await message.reply(name_question)

    # Set state and save initial style
    await state.set_state(OnboardingStates.waiting_for_name)
    await state.update_data(
        current_style=initial_style,
        user_id=user_id,
        username=username,
        all_messages=[]  # Track all messages for style analysis
    )


@onboarding_router.message(OnboardingStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Process user's name input."""
    user_id = message.from_user.id
    name = message.text.strip()

    # Get current data
    data = await state.get_data()

    # Check if we're awaiting confirmation for profile update
    if data.get('awaiting_confirmation'):
        if name.lower() in ['да', 'yes', 'ия', 'иә', 'ok', 'окей']:
            # User confirmed, proceed with update
            await state.update_data(awaiting_confirmation=False)
            initial_style = data.get('current_style', style_detector.analyze_style(""))
            name_question = OnboardingQuestions.get_name_question(initial_style)
            await message.reply(name_question)
            return
        else:
            # User cancelled
            await message.reply("Обновление отменено. Ваш профиль сохранён.")
            await state.clear()
            return

    # Validate name
    if len(name) < 2:
        await message.reply("Пожалуйста, введите корректное имя (минимум 2 символа)")
        return

    if len(name) > 50:
        await message.reply("Имя слишком длинное. Пожалуйста, введите имя покороче.")
        return

    logger.info(f"User {user_id} provided name: {name}")

    # Detect style from this message
    message_style = style_detector.analyze_style(message.text)

    # Update messages list for final style analysis
    messages = data.get('all_messages', [])
    messages.append(message.text)

    # Ask next question
    age_question = OnboardingQuestions.get_age_question(message_style, name)
    await message.reply(age_question)

    # Update state
    await state.set_state(OnboardingStates.waiting_for_age)
    await state.update_data(
        name=name,
        current_style=message_style,
        all_messages=messages
    )


@onboarding_router.message(OnboardingStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Process user's age input."""
    user_id = message.from_user.id
    age_text = message.text.strip()

    # Validate age
    try:
        age = int(age_text)
        if age < 10 or age > 100:
            await message.reply(
                "Пожалуйста, введите корректный возраст (от 10 до 100 лет)"
            )
            return
    except ValueError:
        await message.reply(
            "Пожалуйста, введите возраст числом (например: 25)"
        )
        return

    logger.info(f"User {user_id} provided age: {age}")

    # Get current data and detect style
    data = await state.get_data()
    message_style = style_detector.analyze_style(message.text)

    # Update messages list
    messages = data.get('all_messages', [])
    messages.append(message.text)

    # Ask next question
    goals_question = OnboardingQuestions.get_goals_question(message_style)
    await message.reply(goals_question)

    # Update state
    await state.set_state(OnboardingStates.waiting_for_goals)
    await state.update_data(
        age=age,
        current_style=message_style,
        all_messages=messages
    )


@onboarding_router.message(OnboardingStates.waiting_for_goals)
async def process_goals(message: Message, state: FSMContext):
    """Process user's goals input."""
    user_id = message.from_user.id
    goals = message.text.strip()

    # Validate goals
    if len(goals) < 10:
        await message.reply(
            "Пожалуйста, опишите свои цели подробнее (минимум 10 символов)"
        )
        return

    if len(goals) > 1000:
        await message.reply(
            "Описание слишком длинное. Пожалуйста, сократите до 1000 символов."
        )
        return

    logger.info(f"User {user_id} provided goals: {goals[:50]}...")

    # Get current data and detect style
    data = await state.get_data()
    message_style = style_detector.analyze_style(message.text)

    # Update messages list
    messages = data.get('all_messages', [])
    messages.append(message.text)

    # Ask next question
    language_question = OnboardingQuestions.get_language_question(message_style)
    await message.reply(language_question)

    # Update state
    await state.set_state(OnboardingStates.waiting_for_language)
    await state.update_data(
        goals=goals,
        current_style=message_style,
        all_messages=messages
    )


@onboarding_router.message(OnboardingStates.waiting_for_language)
async def process_language(message: Message, state: FSMContext):
    """Process user's language preference and complete onboarding."""
    user_id = message.from_user.id
    language_input = message.text.strip().lower()

    # Map input to language
    russian_keywords = ['русский', 'русск', 'rus', 'russian', 'ру']
    kazakh_keywords = ['казахский', 'казах', 'қазақ', 'қазақша', 'kaz', 'kazakh', 'каз', 'кз']

    if any(kw in language_input for kw in russian_keywords):
        preferred_language = 'russian'
    elif any(kw in language_input for kw in kazakh_keywords):
        preferred_language = 'kazakh'
    else:
        await message.reply(
            "Пожалуйста, выберите язык: 'русский' или 'казахский'\n"
            "Тілді таңдаңыз: 'орыс' немесе 'қазақ'"
        )
        return

    logger.info(f"User {user_id} selected language: {preferred_language}")

    # Get all collected data
    data = await state.get_data()
    messages = data.get('all_messages', [])
    messages.append(message.text)

    # Analyze overall communication style from all messages
    combined_text = " ".join(messages)
    final_style = style_detector.analyze_style(combined_text)

    # Override language with user's explicit preference
    final_style['language'] = preferred_language

    # Prepare user profile
    user_profile = {
        'user_id': user_id,
        'username': data.get('username'),
        'name': data.get('name'),
        'age': data.get('age'),
        'goals': data.get('goals'),
        'preferred_language': preferred_language,
        'communication_style': final_style,
        'onboarding_completed': True,
        'onboarding_date': message.date.isoformat() if message.date else None
    }

    # Save to storage
    storage.save_user_data(user_id, user_profile)
    logger.info(f"User {user_id} completed onboarding. Profile saved.")

    # Send completion message
    completion_msg = OnboardingQuestions.get_completion_message(
        final_style,
        data.get('name')
    )
    await message.reply(completion_msg)

    # Clear FSM state
    await state.clear()


@onboarding_router.message(Command("profile"))
async def show_profile(message: Message):
    """Display user's profile information."""
    user_id = message.from_user.id

    # Load user data
    user_data = storage.load_user_data(user_id)

    if not user_data or not user_data.get('onboarding_completed'):
        await message.reply(
            "У вас ещё нет профиля. Используйте /onboarding чтобы создать его.\n\n"
            "Сізде әлі профиль жоқ. Жасау үшін /onboarding пайдаланыңыз."
        )
        return

    # Get user's communication style for adapted message
    style = user_data.get('communication_style', {})
    language = style.get('language', 'russian')
    formality = style.get('formality', 'casual')

    # Format profile message
    name = user_data.get('name', 'Не указано')
    age = user_data.get('age', 'Не указано')
    goals = user_data.get('goals', 'Не указано')
    pref_lang = user_data.get('preferred_language', 'Не указано')

    if language == 'kazakh':
        if formality == 'formal':
            header = f"📋 Сіздің профиліңіз:\n"
        else:
            header = f"📋 Сенің профиліңіз:\n"

        profile_text = (
            f"{header}\n"
            f"👤 Аты: {name}\n"
            f"🎂 Жасы: {age}\n"
            f"🎯 Мақсаттар: {goals}\n"
            f"🌐 Тілі: {pref_lang}\n"
            f"💬 Қарым-қатынас стилі: {formality}\n\n"
            f"Профильді өзгерту үшін /onboarding пайдаланыңыз"
        )
    else:
        if formality == 'formal':
            header = f"📋 Ваш профиль:\n"
        else:
            header = f"📋 Твой профиль:\n"

        profile_text = (
            f"{header}\n"
            f"👤 Имя: {name}\n"
            f"🎂 Возраст: {age}\n"
            f"🎯 Цели: {goals}\n"
            f"🌐 Предпочитаемый язык: {pref_lang}\n"
            f"💬 Стиль общения: {formality}\n\n"
            f"Для обновления профиля используйте /onboarding"
        )

    await message.reply(profile_text)
    logger.info(f"User {user_id} viewed their profile")


@onboarding_router.message(Command("cancel"))
async def cancel_onboarding(message: Message, state: FSMContext):
    """Cancel onboarding process."""
    current_state = await state.get_state()

    if current_state is None:
        await message.reply(
            "Нет активного процесса для отмены.\n"
            "Белсенді процесс жоқ."
        )
        return

    await state.clear()
    await message.reply(
        "Процесс отменён. Вы можете начать заново с /onboarding\n\n"
        "Процесс тоқтатылды. /onboarding арқылы қайта бастай аласыз"
    )

    logger.info(f"User {message.from_user.id} cancelled onboarding")
