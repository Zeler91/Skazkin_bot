from src.bot.keyboards import get_main_keyboard, get_tts_keyboard

def test_main_keyboard_structure():
    kb = get_main_keyboard().keyboard
    assert any("Про животных" in btn.text for row in kb for btn in row)


def test_tts_keyboard_structure():
    kb = get_tts_keyboard().inline_keyboard
    assert kb[0][0].callback_data == "tts_request"
