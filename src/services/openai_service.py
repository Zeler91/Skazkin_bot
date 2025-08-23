# src/services/openai_service.py
import logging
from typing import Optional
from config.settings import config
from .story_generator import StoryGenerator, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class OpenAIService(StoryGenerator):
    """Реализация через OpenAI API (совместимый клиент)."""
    def __init__(self):
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise RuntimeError("Не установлен пакет 'openai'. Добавьте его в requirements.txt") from e

        if not config.openai.API_KEY:
            logger.warning("OPENAI_API_KEY не задан — OpenAIService будет неактивен.")

        base_url = config.openai.BASE_URL or None  # можно переопределять для прокси/совместимых API
        self.client = OpenAI(api_key=config.openai.API_KEY, base_url=base_url)

        # модель по умолчанию
        self.model = config.openai.MODEL or "gpt-4o-mini"

    def generate_story(self, prompt: str) -> Optional[str]:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.openai.TEMPERATURE,
                max_tokens=config.openai.MAX_TOKENS,
            )
            text = resp.choices[0].message.content if resp and resp.choices else None
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"OpenAI ошибка: {e}")
            return None
