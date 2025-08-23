"""
Утилиты для форматирования текста сказки под Telegram.
— Аккуратно извлекаем заголовок и тело
— Чистим пунктуацию
— Разбиваем на абзацы
— Готовим Markdown-разметку (ParseMode.MARKDOWN)
"""
from __future__ import annotations
import re
from typing import List, Tuple

# Надёжные маркеры начала основной части сказки (регистронезависимо).
# ВНИМАНИЕ: предлоги "в"/"во" сами по себе не используются — только в устойчивых выражениях.
_STARTER_PATTERNS = [
    r"\bЖили[- ]были\b",
    r"\bЖила[- ]была\b",
    r"\bЖил[- ]был\b",
    r"\bОднажды\b",
    r"\bКак[- ]то раз\b",
    r"\bВ (одном|дал[её]ком|дал[её]кой|старом|тихом|волшебном|маленьком|большом)\b",
    r"\bИ вот однажды\b",
    r"\bС тех пор\b",
]

_STARTER_REGEXES = [re.compile(pat, re.IGNORECASE) for pat in _STARTER_PATTERNS]


def _sanitize_newlines(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Нормализуем множественные пустые строки до одной
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def clean_story_text(text: str) -> str:
    """
    Базовая очистка текста:
    — Нормализация переводов строк
    — Удаление латиницы (если просочилась) — без цифр и знаков препинания
    — Починка пробелов перед/после пунктуации
    — Сведение множественных точек к многоточию
    — Удаление повторов знаков
    """
    if not text:
        return ""

    text = _sanitize_newlines(text)

    # Удаляем латинские фрагменты (слова из >=2 латинских букв).
    # Не трогаем цифры/пунктуацию.
    text = re.sub(r"(?i)\b[a-z]{2,}\b", "", text)

    # Убираем лишние пробелы
    text = re.sub(r"[ \t]+", " ", text)

    # Пробелы перед пунктуацией -> убрать
    text = re.sub(r"\s+([.,!?…])", r"\1", text)
    # Пробел после открывающих кавычек/скобок
    text = re.sub(r"([«(])\s+", r"\1", text)
    # Пробел перед закрывающими кавычками/скобками
    text = re.sub(r"\s+([»)])", r"\1", text)

    # Многоточия
    text = re.sub(r"(\.\s*){3,}", "…", text)

    # Повторы знаков пунктуации
    text = re.sub(r"([.!?…])\1{1,}", r"\1", text)

    # Сдвоенные пробелы → один
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()


def _detect_bold_title_at_start(text: str) -> Tuple[str | None, str]:
    """
    Если модель уже вывела заголовок жирным (*...* или **...**),
    аккуратно достаём его. Поддерживаем варианты: заголовок на своей строке,
    либо заголовок и текст в одной строке.
    """
    # **Заголовок**\n\nТекст
    m = re.match(r"^\s*(\*{2})(.+?)\1\s*\n+\s*(.*)$", text, flags=re.DOTALL)
    if m:
        title = m.group(2).strip()
        body = m.group(3).strip()
        return title, body

    # *Заголовок*\nТекст
    m = re.match(r"^\s*(\*)(.+?)\1\s*\n+\s*(.*)$", text, flags=re.DOTALL)
    if m:
        title = m.group(2).strip()
        body = m.group(3).strip()
        return title, body

    # **Заголовок** Текст (в одной строке)
    m = re.match(r"^\s*(\*{2})(.+?)\1\s*(.+)$", text, flags=re.DOTALL)
    if m:
        return m.group(2).strip(), m.group(3).strip()

    # *Заголовок* Текст (в одной строке)
    m = re.match(r"^\s*(\*)(.+?)\1\s*(.+)$", text, flags=re.DOTALL)
    if m:
        return m.group(2).strip(), m.group(3).strip()

    return None, text


def _split_by_first_sentence(text: str) -> Tuple[str, str]:
    """
    Делим по первому завершающему знаку (. ! ? …).
    Возвращаем (кандидат_заголовок, остальной_текст).
    Если знаков нет — берём первые ~6 слов.
    """
    m = re.search(r"([.!?…])", text)
    if m:
        pos = m.end()
        return text[:pos].strip(), text[pos:].strip()

    words = text.split()
    title = " ".join(words[:6]).strip()
    body = " ".join(words[6:]).strip()
    return title, body


def _clip_long_title_with_starters(full_text: str, title: str) -> Tuple[str, str]:
    """
    Если заголовок подозрительно длинный — ищем «маркеры начала сказки» и режем по ним.
    """
    # Ищем первый надёжный маркер не в самом начале
    lower_text = full_text
    best_pos = None
    for rx in _STARTER_REGEXES:
        m = rx.search(lower_text)
        if m and m.start() > 3:
            if best_pos is None or m.start() < best_pos:
                best_pos = m.start()

    if best_pos:
        new_title = full_text[:best_pos].strip()
        new_body = full_text[best_pos:].strip()
        # Снимаем хвосты пунктуации у заголовка
        new_title = re.sub(r"[.,!?…\s]+$", "", new_title)
        return new_title, new_body

    # Иначе возвращаем как есть
    return title, full_text[len(title):].strip() if full_text.startswith(title) else (title, full_text)


def extract_story_title_and_body(story_text: str) -> Tuple[str, str]:
    """
    Главный алгоритм извлечения заголовка и тела сказки.
    1) Чистим текст
    2) Пробуем выдернуть уже-жирный заголовок (*...*/**...**)
    3) Иначе режем по первому предложению
    4) Если заголовок слишком длинный (>12 слов), пробуем найти маркер начала
    """
    text = clean_story_text(story_text)

    # 1) Уже-жирный заголовок?
    title, rest = _detect_bold_title_at_start(text)
    if title:
        # Снимаем хвосты пунктуации и лишние звёздочки/подчёркивания внутри заголовка
        title = re.sub(r"[.,!?…\s]+$", "", title)
        title = title.replace("*", "").replace("_", "").strip()
        return title, rest

    # 2) Делим по первому предложению
    candidate_title, body = _split_by_first_sentence(text)

    # Снимаем хвосты пунктуации у заголовка
    candidate_title = re.sub(r"[.,!?…\s]+$", "", candidate_title)

    # 3) Если заголовок слишком длинный — ищем стартовые маркеры
    if len(candidate_title.split()) > 12:
        candidate_title, body = _clip_long_title_with_starters(text, candidate_title)

    # Фоллбэк: если заголовок пустой — берём первые 4–6 слов
    if not candidate_title:
        words = text.split()
        candidate_title = " ".join(words[:6]).strip()
        body = " ".join(words[6:]).strip()

    # Ещё раз подчистим пробелы
    candidate_title = re.sub(r"\s{2,}", " ", candidate_title).strip()
    body = body.strip()

    return candidate_title, body


def _escape_legacy_markdown(text: str) -> str:
    """
    Telegram ParseMode.MARKDOWN (legacy) конфликтует со знаками: *, _, `, [.
    Титул мы форматируем сами, поэтому в теле: заменяем проблемные символы.
    """
    # Заменяем звёздочки/подчёркивания, чтобы не ломать разметку
    text = text.replace("*", "✱")
    text = text.replace("_", " ")
    text = text.replace("`", "ʼ")
    text = text.replace("[", "〖").replace("]", "〗")
    return text


def split_into_paragraphs(text: str, sentences_per_paragraph: int = 2) -> List[str]:
    """
    Разбиение на абзацы по 2–3 предложения.
    Учитываем русские кавычки/заглавные начала предложений.
    """
    if not text:
        return []

    # Нормализуем пробелы вокруг кавычек
    text = re.sub(r"\s+([»)])", r"\1", text)
    text = re.sub(r"([«(])\s+", r"\1", text)

    # Сплит предложений: после . ! ? … + пробел(ы) + следующее предложение начинается с заглавной/кавычек/тире
    sentences = re.split(r'(?<=[.!?…])\s+(?=[«"“(—\-]*[А-ЯЁ])', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    paragraphs: List[str] = []
    buf: List[str] = []

    for s in sentences:
        buf.append(s)
        if len(buf) >= sentences_per_paragraph:
            paragraphs.append(" ".join(buf))
            buf = []

    if buf:
        paragraphs.append(" ".join(buf))

    # Финальная чистка повторных пробелов
    paragraphs = [re.sub(r"\s{2,}", " ", p).strip() for p in paragraphs]
    return paragraphs


def format_story_for_telegram(story_text: str) -> str:
    """
    Итоговое форматирование под Telegram (ParseMode.MARKDOWN):
    *Заголовок*

    Абзац 1

    Абзац 2
    """
    title, body = extract_story_title_and_body(story_text)

    # Титул — без проблемных Markdown-символов
    safe_title = title.replace("*", "").replace("_", "").strip()
    if not safe_title:
        safe_title = "Сказка"

    # Тело — экранируем опасные для Markdown символы
    safe_body = _escape_legacy_markdown(body)

    paragraphs = split_into_paragraphs(safe_body)
    if paragraphs:
        return f"*{safe_title}*\n\n" + "\n\n".join(paragraphs)
    else:
        return f"*{safe_title}*"


def extract_story_title(story_text: str) -> str:
    """
    Вспомогательная функция — только заголовок (для имени файла TTS и т.п.).
    """
    title, _ = extract_story_title_and_body(story_text)
    # Без опасных символов и с ограничением длины
    title = re.sub(r"[^\w\s\-]", "", title, flags=re.UNICODE)
    title = re.sub(r"\s{2,}", " ", title).strip()
    return title[:50] if len(title) > 50 else title


def truncate_text(text: str, max_length: int = 2000) -> str:
    """
    Обрезка до max_length с попыткой завершить на конце предложения.
    """
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]
    last_end = max(
        truncated.rfind("."),
        truncated.rfind("!"),
        truncated.rfind("?"),
        truncated.rfind("…"),
    )
    if last_end > int(max_length * 0.8):
        return truncated[: last_end + 1]

    return truncated.rstrip() + "…"
