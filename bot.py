import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# === 1. ТВОЙ ТОКЕН И ИНИЦИАЛИЗАЦИЯ ===
# Вставь сюда свой токен от BotFather (в кавычках)
BOT_TOKEN = "8913122681:AAHJECRiOevBLLHw9xsbPJUdVlQUV5aQPRk" 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === 2. КЛАВИАТУРЫ И НАСТРОЙКИ (ВСЁ, ЧТО МЫ ДЕЛАЛИ) ===
# Пример твоей кнопки «Очистить память»
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🧹 Очистить память")]],
    resize_keyboard=True
)

# === 3. ХЕНДЛЕРЫ И ЛОГИКА БОТА ===

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! 😊\nЕсли у тебя есть вопросы, спрашивай! Я готов помочь. 🍕✨",
        reply_markup=main_kb
    )

# Обработка кнопки «Очистить память»
@dp.message(F.text == "🧹 Очистить память")
async def clear_memory(message: Message):
    # Здесь твоя логика очистки памяти (если была в коде)
    await message.answer("Память успешно очищена!", reply_markup=main_kb)

# Основной обработчик сообщений (твоя логика с ИИ)
@dp.message()
async def handle_message(message: Message):
    # Сюда подключается твой ИИ (OpenAI / Google Gemini / или другая либа)
    # Пример простого эха или ответа:
    user_text = message.text
    
    # Твой код взаимодействия с ИИ пиши здесь:
    # response = ai_model.generate(user_text)
    
    await message.answer(f"Привет! Если у тебя есть вопросы о пицце, сырах, рецептах или чем-то ещё — спрашивай! Я готов помочь. 🍕✨\n\n(И да, если ты просто здоровался — я тоже! 👋)")


# === 4. ВЕБ-СЕРВЕР ДЛЯ RENDER И CRON-JOB (ЧТОБЫ БОТ НЕ ЗАСЫПАЛ) ===
async def handle_ping(request):
    return web.Response(text="Bot is alive!")


async def main():
    # Запускаем локальный мини-сервер для пингов от cron-job.org
    app = web.Application()
    app.router.add_get("/", handle_ping)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print("Веб-сервер и бот успешно запущены!")
    
    # Запускаем опрос Telegram
    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())
