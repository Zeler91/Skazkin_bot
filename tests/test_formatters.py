import pytest
from src.utils.formatters import (
    format_story_for_telegram,
    extract_story_title,
)

# === Тесты ===

def test_bold_title_with_body():
    """
    Случай: модель вывела заголовок жирным и перенесла текст на новую строку.
    """
    story = "**Белоснежный лес.**\n\nЖили-были зверята..."
    formatted = format_story_for_telegram(story)
    assert formatted.startswith("*Белоснежный лес*")
    assert "Жили-были зверята" in formatted


def test_inline_bold_title_and_body():
    """
    Случай: модель вывела заголовок жирным и сразу начала текст в той же строке.
    """
    story = "**Смешной зайчонок.** В лесу жил..."
    formatted = format_story_for_telegram(story)
    assert formatted.startswith("*Смешной зайчонок*")
    assert "В лесу жил" in formatted


def test_no_bold_title_first_sentence_as_title():
    """
    Случай: модель не выделила заголовок — берём первое предложение.
    """
    story = "Храбрый мышонок отправился в путь. Жили-были..."
    formatted = format_story_for_telegram(story)
    assert formatted.startswith("*Храбрый мышонок отправился в путь*")
    assert "Жили-были" in formatted


def test_too_long_title_clip_with_marker():
    """
    Случай: заголовок слишком длинный, режем по маркеру 'Жили-были'.
    """
    story = "История о девочке которая долго искала дом и друзей Жили-были кот и пёс..."
    title = extract_story_title(story)
    assert "История о девочке" in title
    assert "Жили-были" not in title


def test_safe_markdown_symbols():
    """
    Случай: в тексте есть * _ [] ` — должны быть заменены на безопасные символы.
    """
    story = "Сказка про символы. Жили-были [герои] *звёздные* и _подчёркнутые_."
    formatted = format_story_for_telegram(story)
    assert "〖герои〗" in formatted
    assert "✱звёздные✱" in formatted
    assert "подчёркнутые" in formatted  # подчёркивания убираются
    assert "ʼ" not in formatted  # проверка на обратные кавычки


def test_extract_title_short_fallback():
    """
    Случай: если текста мало, берём первые несколько слов.
    """
    story = "Просто начало без конца"
    title = extract_story_title(story)
    assert title.startswith("Просто начало")
