"""
Обработчики для Telegram бота
"""
import time
import logging
from collections import defaultdict
from typing import Dict, Any

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config.settings import config
from src.services.story_generator_factory import get_story_generator
from src.services.tts_service import tts_service
from src.utils.formatters import format_story_for_telegram, truncate_text, extract_story_title
from src.bot.keyboards import get_main_keyboard, get_tts_keyboard, get_story_actions_keyboard

logger = logging.getLogger(__name__)

# Хранилище состояния пользователей
user_cooldowns: Dict[int, float] = defaultdict(float)
user_states: Dict[int, str] = defaultdict(str)
user_last_story: Dict[int, str] = defaultdict(str)

class StoryBotHandlers:
    """Обработчики для бота сказок"""
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        keyboard = get_main_keyboard()
        await update.message.reply_text(
            "👋 Привет! Я Сказкин — бот, который сочиняет сказки на любую тему! ✨\n\n"
            "Выбери тему сказки или напиши свою.",
            reply_markup=keyboard
        )
    
    @staticmethod
    async def send_story(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
        await update.message.reply_text("📝 Пишу сказку...")

        story_generator = get_story_generator()
        story = story_generator.generate_story(prompt)

        if not story:
            await update.message.reply_text(config.errors.GENERIC_ERROR)
            return

        formatted_story = format_story_for_telegram(story)

        if len(formatted_story) > config.bot.MAX_STORY_LENGTH:
            formatted_story = truncate_text(formatted_story, config.bot.MAX_STORY_LENGTH)

        user_last_story[update.effective_user.id] = story

        await update.message.reply_text(formatted_story, parse_mode=ParseMode.MARKDOWN)

        if tts_service.is_available():
            keyboard = get_tts_keyboard()
            await update.message.reply_text("Хочешь, озвучу сказку? 🎙", reply_markup=keyboard)
            
    @staticmethod
    async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик запроса на TTS"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        story = user_last_story.get(user_id)
        
        if not story:
            await query.edit_message_text("Сначала закажи сказку.")
            return
        
        await query.edit_message_text("🎙 Озвучиваю сказку...")
        
        try:
            # Извлекаем название сказки
            story_title = extract_story_title(story)
            
            # Синтезируем речь с названием сказки
            result = tts_service.synthesize_speech(story, story_title)
            
            if result:
                audio_data, temp_filename = result
                
                try:
                    # Отправляем аудио с названием сказки
                    with open(temp_filename, "rb") as audio_file:
                        await query.message.reply_audio(
                            audio_file, 
                            caption=f"📖 {story_title}"
                        )
                finally:
                    # Удаляем временный файл
                    tts_service.cleanup_temp_file(temp_filename)
            else:
                await query.message.reply_text(config.errors.TTS_ERROR)
                
        except Exception as e:
            logger.error(f"Ошибка TTS: {e}")
            await query.message.reply_text(config.errors.TTS_ERROR)
    
    @staticmethod
    async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        user_id = update.effective_user.id
        now = time.time()
        
        # Проверяем кулдаун
        if now - user_cooldowns[user_id] < config.bot.COOLDOWN_SECONDS:
            await update.message.reply_text("⏳ Подожди немного.")
            return
        
        user_cooldowns[user_id] = now
        topic = update.message.text.strip()
        
        # Словарь промптов для кнопок
        prompts = {
            "🐾 Про животных": "Придумай сказку про необычных животных.",
            "🏝 Про приключения": "Придумай сказку о детях в путешествии.",
            "🔮 Про волшебство": "Придумай волшебную сказку с чудесами."
        }
        
        # Обработка кнопки "Про любимого героя"
        if topic == "🌟 Про любимого героя":
            user_states[user_id] = "awaiting_hero_description"
            await update.message.reply_text("Опиши любимого героя.")
            return
        
        # Обработка остальных кнопок
        if prompt := prompts.get(topic):
            await StoryBotHandlers.send_story(update, context, prompt)
    
    @staticmethod
    async def handle_custom_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик пользовательского текста"""
        user_id = update.effective_user.id
        user_input = update.message.text.strip()
        
        # Обработка описания героя (без кулдауна)
        if user_states.get(user_id) == "awaiting_hero_description":
            user_states[user_id] = ""
            prompt = f"Придумай сказку с героем: {user_input}"
            await StoryBotHandlers.send_story(update, context, prompt)
            return
        
        # Для остальных запросов проверяем кулдаун
        now = time.time()
        if now - user_cooldowns[user_id] < config.bot.COOLDOWN_SECONDS:
            await update.message.reply_text("⏳ Подожди немного.")
            return
        
        user_cooldowns[user_id] = now
        prompt = user_input
        
        await StoryBotHandlers.send_story(update, context, prompt)
    
    @staticmethod
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error("Ошибка в боте:", exc_info=context.error)
        
        # Отправляем сообщение об ошибке пользователю
        if update and hasattr(update, 'message') and update.message:
            await update.message.reply_text(config.errors.DEFAULT)
