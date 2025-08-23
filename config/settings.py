# config/settings.py
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    COOLDOWN_SECONDS: int = 8
    MAX_STORY_LENGTH: int = 3500

@dataclass
class ErrorsConfig:
    GENERIC_ERROR: str = "Не удалось сгенерировать сказку. Попробуй ещё раз."
    TTS_ERROR: str = "Не удалось озвучить сказку сейчас. Попробуй позже."
    DEFAULT: str = "Произошла ошибка, мы уже чиним 🛠"

@dataclass
class GigaChatConfig:
    AUTH_KEY: str = os.getenv("GIGACHAT_AUTH_KEY", "")
    SCOPE: str = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    MODEL: str = os.getenv("GIGACHAT_MODEL", "GigaChat-2")
    TIMEOUT: int = int(os.getenv("GIGACHAT_TIMEOUT", "40"))
    TEMPERATURE: float = float(os.getenv("GIGACHAT_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("GIGACHAT_MAX_TOKENS", "1200"))

@dataclass
class OpenAIConfig:
    API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")  # опционально
    MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1200"))

@dataclass
class DeepSeekConfig:
    API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("DEEPSEEK_MAX_TOKENS", "1200"))

@dataclass
class GeminiConfig:
    API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "1200"))

@dataclass
class LLMConfig:
    PROVIDER: str = os.getenv("LLM_PROVIDER", "gigachat")  # gigachat|openai|deepseek|gemini

@dataclass
class TTSConfig:
    API_KEY: str = os.getenv("YANDEX_TTS_API_KEY", "")
    LANGUAGE: str = "ru-RU"
    VOICE: str = "jane"
    EMOTION: str = "good"
    SPEED: str = "1.0"
    FORMAT: str = "mp3"

@dataclass
class AppConfig:
    bot: BotConfig = BotConfig()
    errors: ErrorsConfig = ErrorsConfig()
    gigachat: GigaChatConfig = GigaChatConfig()
    openai: OpenAIConfig = OpenAIConfig()
    deepseek: DeepSeekConfig = DeepSeekConfig()
    gemini: GeminiConfig = GeminiConfig()
    tts: TTSConfig = TTSConfig()
    llm: LLMConfig = LLMConfig()

    def validate(self):
        if not self.bot.TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не задан")
        # Предупреждаем, если у выбранного провайдера нет ключа
        provider = self.llm.PROVIDER.lower()
        if provider == "gigachat" and not self.gigachat.AUTH_KEY:
            raise ValueError("GIGACHAT_AUTH_KEY не задан для выбранного провайдера gigachat")
        if provider == "openai" and not self.openai.API_KEY:
            raise ValueError("OPENAI_API_KEY не задан для выбранного провайдера openai")
        if provider == "deepseek" and not self.deepseek.API_KEY:
            raise ValueError("DEEPSEEK_API_KEY не задан для выбранного провайдера deepseek")
        if provider == "gemini" and not self.gemini.API_KEY:
            raise ValueError("GEMINI_API_KEY не задан для выбранного провайдера gemini")

config = AppConfig()
