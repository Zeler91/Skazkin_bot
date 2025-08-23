"""
Клавиатуры для Telegram бота
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура с темами сказок"""
    keyboard = [
        [KeyboardButton("🐾 Про животных"), KeyboardButton("🏝 Про приключения")],
        [KeyboardButton("🔮 Про волшебство"), KeyboardButton("🌟 Про любимого героя")]
    ]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите тему или напишите свою"
    )

def get_tts_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для TTS запроса"""
    keyboard = [
        [InlineKeyboardButton("🎧 Хочу послушать", callback_data="tts_request")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_story_actions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с действиями для сказки"""
    keyboard = [
        [
            InlineKeyboardButton("🎧 Озвучить", callback_data="tts_request"),
            InlineKeyboardButton("📝 Новая сказка", callback_data="new_story")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
