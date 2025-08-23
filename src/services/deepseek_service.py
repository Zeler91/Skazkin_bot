# src/services/deepseek_service.py
import logging
from typing import Optional
from config.settings import config
from .story_generator import StoryGenerator, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class DeepSeekService(StoryGenerator):
    """Реализация через DeepSeek API (OpenAI-совместимый)."""
    def __init__(self):
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise RuntimeError("Не установлен пакет 'openai'. Добавьте его в requirements.txt") from e

        if not config.deepseek.API_KEY:
            logger.warning("DEEPSEEK_API_KEY не задан — DeepSeekService будет неактивен.")

        # DeepSeek использует OpenAI-совместимый endpoint
        base_url = config.deepseek.BASE_URL or "https://api.deepseek.com"
        self.client = OpenAI(api_key=config.deepseek.API_KEY, base_url=base_url)

        self.model = config.deepseek.MODEL or "deepseek-chat"

    def generate_story(self, prompt: str) -> Optional[str]:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.deepseek.TEMPERATURE,
                max_tokens=config.deepseek.MAX_TOKENS,
            )
            text = resp.choices[0].message.content if resp and resp.choices else None
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"DeepSeek ошибка: {e}")
            return None
