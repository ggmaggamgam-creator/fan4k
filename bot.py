import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import g4f

# Твой токен Telegram-бота
TOKEN = "8913122681:AAGpY0WQEmGCDdrNjke-djWJfjoAJ0lYjX8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Хранилище истории сообщений для каждого пользователя
user_histories = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer(
        "Привет! Твой бот полностью запущен и работает без лимитов 🚀✨\n\n"
        "• Пиши любые вопросы и общайся с памятью сколько угодно\n"
        "• Команда /draw <описание> создаст для тебя крутую картинку\n"
        "• Команда /clear очистит историю диалога"
    )

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer("🧹 История нашего разговора полностью очищена!")

@dp.message(Command("draw"))
async def cmd_draw(message: types.Message):
    prompt = message.text.replace("/draw", "").strip()
    
    if not prompt:
        await message.answer("Пожалуйста, напиши описание после команды, например: /draw кот в космосе")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")

    try:
        image_response = await asyncio.to_thread(
            g4f.ImageGeneration.create,
            prompt=prompt,
            model=g4f.models.gemini_pro
        )
        
        if image_response:
            await message.answer_photo(image_response, caption=f"🎨 Твой запрос: {prompt}")
        else:
            await message.answer("Не удалось сгенерировать картинку. Попробуй другое описание!")

    except Exception as e:
        print(f"Ошибка генерации картинки: {e}")
        try:
            fallback_desc = await asyncio.to_thread(
                g4f.ChatCompletion.create,
                model=g4f.models.default,
                messages=[{"role": "user", "content": f"Опиши подробно картину для генерации: {prompt}"}]
            )
            await message.answer(f"🎨 Идея для рисунка:\n\n{fallback_desc}")
        except:
            await message.answer("Произошла ошибка при создании картинки. Попробуй еще раз!")

@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "content": message.text})

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = await asyncio.to_thread(
            g4f.ChatCompletion.create,
            model=g4f.models.default,
            messages=user_histories[user_id]
        )

        user_histories[user_id].append({"role": "assistant", "content": response})

        await message.answer(response)

    except Exception as e:
        print(f"Ошибка запроса: {e}")
        await message.answer("Произошла небольшая задержка сети. Попробуй отправить сообщение ещё раз!")


# --- ВЕБ-СЕРВЕР ДЛЯ RENDER И CRON-JOB (ЧТОБЫ БОТ РАБОТАЛ 24/7) ---
async def handle_ping(request):
    return web.Response(text="OK")


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
    
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
