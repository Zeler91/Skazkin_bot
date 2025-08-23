"""
Сервис для работы с Yandex Text-to-Speech API
"""
import os
import logging
import tempfile
from typing import Optional, Tuple
import requests

from config.settings import config

logger = logging.getLogger(__name__)

class TTSService:
    """Сервис для работы с Yandex TTS API"""
    
    def __init__(self):
        self.api_key = config.tts.API_KEY
        self.base_url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        self.enabled = bool(self.api_key)
    
    def is_available(self) -> bool:
        """Проверка доступности TTS сервиса"""
        return self.enabled
    
    def synthesize_speech(self, text: str, title: str = "Сказка") -> Optional[Tuple[bytes, str]]:
        """
        Синтез речи из текста
        
        Args:
            text: Текст для озвучивания
            title: Название сказки для имени файла
            
        Returns:
            Кортеж (аудио_данные, имя_файла) или None в случае ошибки
        """
        if not self.enabled:
            logger.warning("TTS сервис недоступен - не установлен API ключ")
            return None
        
        try:
            headers = {"Authorization": f"Api-Key {self.api_key}"}
            data = {
                "text": text,
                "lang": config.tts.LANGUAGE,
                "voice": config.tts.VOICE,
                "emotion": config.tts.EMOTION,
                "speed": config.tts.SPEED,
                "format": config.tts.FORMAT
            }
            
            response = requests.post(
                self.base_url, 
                headers=headers, 
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                # Создаем временный файл с названием сказки
                import re
                # Очищаем название от недопустимых символов для имени файла
                safe_title = re.sub(r'[^\w\s-]', '', title)
                safe_title = re.sub(r'\s+', '_', safe_title).strip()
                safe_title = safe_title[:30] if len(safe_title) > 30 else safe_title  # Ограничиваем длину
                
                # Создаем временный файл с префиксом названия сказки
                with tempfile.NamedTemporaryFile(
                    prefix=f"{safe_title}_",
                    suffix=".mp3", 
                    delete=False,
                    mode="wb"
                ) as temp_file:
                    temp_file.write(response.content)
                    temp_filename = temp_file.name
                
                logger.info(f"Аудио успешно синтезировано: {len(response.content)} байт, файл: {temp_filename}")
                return response.content, temp_filename
            else:
                logger.error(f"Ошибка TTS API: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Ошибка сети при синтезе речи: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при синтезе речи: {e}")
            return None
    
    def cleanup_temp_file(self, filename: str):
        """Удаление временного файла"""
        try:
            if os.path.exists(filename):
                os.remove(filename)
                logger.debug(f"Временный файл удален: {filename}")
        except Exception as e:
            logger.error(f"Ошибка при удалении временного файла {filename}: {e}")

# Глобальный экземпляр сервиса
tts_service = TTSService()
