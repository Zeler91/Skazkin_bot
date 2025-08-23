# src/services/gemini_service.py
import logging
from typing import Optional
from config.settings import config
from .story_generator import StoryGenerator, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class GeminiService(StoryGenerator):
    """Реализация через Gemini (Google AI)."""
    def __init__(self):
        try:
            import google.generativeai as genai  # type: ignore
        except Exception as e:
            raise RuntimeError("Не установлен пакет 'google-generativeai'. Добавьте его в requirements.txt") from e

        if not config.gemini.API_KEY:
            logger.warning("GEMINI_API_KEY не задан — GeminiService будет неактивен.")

        genai.configure(api_key=config.gemini.API_KEY)
        model_name = config.gemini.MODEL or "gemini-1.5-flash"
        self.model = genai.GenerativeModel(model_name)

    def generate_story(self, prompt: str) -> Optional[str]:
        try:
            # Для Gemini передаём system-prompt в первой реплике вместе
            text_input = f"{SYSTEM_PROMPT}\n\nПользовательская тема: {prompt}"
            resp = self.model.generate_content(text_input)
            # У разных версий SDK способ доступа к тексту немного отличается:
            if hasattr(resp, "text"):
                text = resp.text
            else:
                # fallback
                text = "".join([p.text for p in getattr(resp, "candidates", []) if getattr(p, "text", None)]) or None
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"Gemini ошибка: {e}")
            return None
