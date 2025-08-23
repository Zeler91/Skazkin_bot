# src/services/story_generator_factory.py
from typing import Optional
from config.settings import config
from .story_generator import StoryGenerator
from .gigachat_service import GigaChatService
from .openai_service import OpenAIService
from .deepseek_service import DeepSeekService
from .gemini_service import GeminiService

_singleton: Optional[StoryGenerator] = None

def get_story_generator() -> StoryGenerator:
    global _singleton
    if _singleton:
        return _singleton

    provider = (config.llm.PROVIDER or "gigachat").lower()
    if provider == "gigachat":
        _singleton = GigaChatService()
    elif provider == "openai":
        _singleton = OpenAIService()
    elif provider == "deepseek":
        _singleton = DeepSeekService()
    elif provider == "gemini":
        _singleton = GeminiService()
    else:
        raise ValueError(f"Неизвестный LLM провайдер: {provider}")

    return _singleton
