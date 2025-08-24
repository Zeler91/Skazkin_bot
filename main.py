"""
Главный файл приложения Сказкин бот
"""
import logging
import signal
import sys
import threading
import web_server  # импортируем мини-сервер
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config.settings import config
from src.bot.handlers import StoryBotHandlers
from src.services.gigachat_service import gigachat_service

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def setup_handlers(app):
    """Настройка обработчиков для бота"""
    app.add_handler(CommandHandler("start", StoryBotHandlers.start))
    app.add_handler(MessageHandler(
        filters.Regex(r"^🐾|🏝|🔮|🌟"), 
        StoryBotHandlers.handle_button
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        StoryBotHandlers.handle_custom_text
    ))
    app.add_handler(CallbackQueryHandler(
        StoryBotHandlers.handle_tts_request, 
        pattern="^tts_request$"
    ))
    app.add_error_handler(StoryBotHandlers.error_handler)

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info("Получен сигнал завершения, останавливаю бота...")
    gigachat_service.cleanup()
    sys.exit(0)

def main():
    """Главная функция приложения"""
    try:
        # Проверяем конфигурацию
        config.validate()
        logger.info("Конфигурация проверена успешно")
        
        # Настраиваем обработчики сигналов
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Создаем приложение
        app = ApplicationBuilder().token(config.bot.TOKEN).build()
        
        # Настраиваем обработчики
        setup_handlers(app)
        
        logger.info("Бот запускается...")
        app.run_polling()
        
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        # Очистка ресурсов
        gigachat_service.cleanup()

def run_web_server():
    web_server.app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    # Запускаем сервер в отдельном потоке
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Запускаем бота
    main()

