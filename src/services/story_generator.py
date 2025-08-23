# src/services/story_generator.py
from abc import ABC, abstractmethod
from typing import Optional

SYSTEM_PROMPT = (
    "Ты — добрый сказочник. Пиши короткие добрые сказки для детей 4–6 лет "
    "только на русском языке, без английских слов и латиницы.\n"
    "Структура:\n"
    "1) Первая строка — яркий уникальный заголовок (не слово 'Сказка'), выдели его **жирным**.\n"
    "2) Текст по абзацам (2–3 предложения), между абзацами пустая строка.\n"
    "3) Поучительный, мягкий финал."
)

class StoryGenerator(ABC):
    """Единый интерфейс генераторов сказок для разных LLM."""
    @abstractmethod
    def generate_story(self, prompt: str) -> Optional[str]:
        ...
