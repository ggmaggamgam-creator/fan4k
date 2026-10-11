import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from g4f.client import Client

# === 1. ТОКЕН И ИНИЦИАЛИЗАЦИЯ ===
BOT_TOKEN = "8913122681:AAHJECRiOevBLLHw9xsbPJUdVlQUV5aQPRk"  # Твой токен от BotFather

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клиент g4f для работы с ChatGPT
g4f_client = Client()

# Кнопка «Очистить память»
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🧹 Очистить память")]],
    resize_keyboard=True
)

# === 2. ХЕНДЛЕРЫ БОТА ===

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я твой бот на базе g4f. Задай мне любой вопрос!",
        reply_markup=main_kb
    )

# Обработка кнопки «Очистить память»
@dp.message(F.text == "🧹 Очистить память")
async def clear_memory(message: Message):
    # Здесь можно добавить очистку истории, если она у тебя сохранялась в коде
    await message.answer("Память успешно очищена!", reply_markup=main_kb)

# Основной обработчик сообщений (запросы к g4f ChatGPT)
@dp.message()
async def handle_message(message: Message):
    user_text = message.text
    
    # Показываем пользователю, что бот «печатает»
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Отправляем запрос через g4f (используем gpt-4o или gpt-4)
        response = g4f_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": user_text}]
        )
        ai_reply = response.choices[0].message.content
        await message.answer(ai_reply)
    except Exception as e:
        # Если вдруг бесплатный провайдер g4f временно сбоит
        await message.answer(f"Произошла ошибка при обращении к ИИ: {e}")


# === 3. ВЕБ-СЕРВЕР ДЛЯ RENDER И CRON-JOB (ДЛЯ 24/7) ===
async def handle_ping(request):
    return web.Response(text="OK")


async def main():
    app = web.Application()
    app.router.add_get("/", handle_ping)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print("Веб-сервер и бот с g4f успешно запущены!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
