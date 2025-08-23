# src/services/gigachat_service.py
import time
import logging
from typing import Optional
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from gigachat.exceptions import GigaChatException

from config.settings import config
from .story_generator import StoryGenerator, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class GigaChatService(StoryGenerator):
    """Реализация StoryGenerator для GigaChat."""

    def __init__(self):
        self._token_cache = {"token": None, "expires_at": 0, "client": None}

    def _get_client(self) -> GigaChat:
        now = time.time()
        if (self._token_cache["token"]
            and now < self._token_cache["expires_at"]
            and self._token_cache["client"]):
            return self._token_cache["client"]

        try:
            client = GigaChat(
                credentials=config.gigachat.AUTH_KEY,
                scope=config.gigachat.SCOPE,
                model=config.gigachat.MODEL,
                verify_ssl_certs=False,
                timeout=config.gigachat.TIMEOUT
            )
            client.__enter__()
            self._token_cache.update({
                "token": client.token,
                "expires_at": now + 30 * 60,
                "client": client
            })
            return client
        except Exception as e:
            logger.error(f"Ошибка создания GigaChat клиента: {e}")
            raise

    def generate_story(self, prompt: str) -> Optional[str]:
        try:
            client = self._get_client()
            chat = Chat(
                messages=[
                    Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                    Messages(role=MessagesRole.USER, content=prompt)
                ],
                temperature=config.gigachat.TEMPERATURE,
                max_tokens=config.gigachat.MAX_TOKENS
            )
            response = client.chat(chat)
            story = response.choices[0].message.content
            return story.strip() if story else None
        except GigaChatException as e:
            logger.error(f"GigaChat API ошибка: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка GigaChat: {e}")
            return None

    def cleanup(self):
        if self._token_cache["client"]:
            try:
                self._token_cache["client"].__exit__(None, None, None)
            except Exception as e:
                logger.error(f"Ошибка при закрытии GigaChat клиента: {e}")
            finally:
                self._token_cache = {"token": None, "expires_at": 0, "client": None}

# экспорт совместимости (если где-то ещё импортируется gigachat_service)
gigachat_service = GigaChatService()
