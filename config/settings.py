from dataclasses import dataclass, field
import os

# === Конфигурация бота ===
@dataclass
class BotConfig:
    TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    MAX_STORY_LENGTH: int = 4000
    COOLDOWN_SECONDS: int = 5


# === Конфигурация GigaChat ===
@dataclass
class GigaChatConfig:
    AUTH_KEY: str = os.getenv("GIGACHAT_AUTH_KEY", "")
    SCOPE: str = "GIGACHAT_API_PERS"
    MODEL: str = "GigaChat"
    TIMEOUT: int = 30
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 800


# === Конфигурация TTS ===
@dataclass
class TTSConfig:
    API_KEY: str = os.getenv("YANDEX_API_KEY", "")
    LANGUAGE: str = "ru-RU"
    VOICE: str = "oksana"
    EMOTION: str = "good"
    SPEED: float = 1.0
    FORMAT: str = "mp3"


# === Конфигурация LLM (выбор провайдера) ===
@dataclass
class LLMConfig:
    PROVIDER: str = os.getenv("LLM_PROVIDER", "gigachat")  
    # варианты: "gigachat", "openai", "gemini", "deepseek"


# === Сообщения об ошибках ===
@dataclass
class ErrorMessages:
    GENERIC_ERROR: str = "😔 Что-то пошло не так. Попробуй ещё раз!"
    TTS_ERROR: str = "⚠️ Не удалось озвучить сказку."
    DEFAULT: str = "⚠️ Произошла ошибка."


# === Общая конфигурация ===
@dataclass
class Config:
    bot: BotConfig = field(default_factory=BotConfig)
    gigachat: GigaChatConfig = field(default_factory=GigaChatConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    errors: ErrorMessages = field(default_factory=ErrorMessages)

    def validate(self):
        if not self.bot.TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не задан")
        if not self.gigachat.AUTH_KEY:
            raise ValueError("GIGACHAT_AUTH_KEY не задан")


# === Глобальный объект ===
config = Config()
