import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import g4f

TOKEN = "8913122681:AAHJECRiOevBLLHw9xsbPJUdVlQUV5aQPRk"

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

user_histories = {}

# Создаем постоянную клавиатуру под строкой ввода текста в Telegram
clear_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧹 Очистить память")]
    ],
    resize_keyboard=True  # Делает кнопку аккуратной и компактной по размеру экрана
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer(
        "Привет! Твой бот полностью готов и работает без лимитов 🤖✨\n\n"
        "• Отправляй текст, вопросы или файлы\n"
        "• Используй кнопку «🧹 Очистить память» внизу экрана",
        reply_markup=clear_keyboard
    )

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer("🧹 История диалога очищена!", reply_markup=clear_keyboard)

@dp.message(F.text == "🧹 Очистить память")
async def handle_clear_button(message: types.Message):
    user_histories[message.from_user.id] = []
    await message.answer("🧹 История нашего разговора успешно очищена!", reply_markup=clear_keyboard)

@dp.message(F.text | F.photo | F.video | F.voice | F.document)
async def handle_all_media(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_histories:
        user_histories[user_id] = []

    # 1. Отправляем эмодзи робота (🤖) как индикатор того, что бот думает
    loading_msg = await message.answer("🤖")
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Формируем текст запроса
    user_text = message.text or message.caption or "Опиши или ответь на этот файл/медиа."
    user_histories[user_id].append({"role": "user", "content": user_text})

    try:
        # Запрос к нейросети
        response = await asyncio.to_thread(
            g4f.ChatCompletion.create,
            model=g4f.models.default,
            messages=user_histories[user_id]
        )

        user_histories[user_id].append({"role": "assistant", "content": response})

        # 2. Удаляем сообщение с эмодзи робота перед отправкой ответа
        try:
            await loading_msg.delete()
        except:
            pass

        # Отправляем готовый ответ пользователю
        await message.answer(response, reply_markup=clear_keyboard)

    except Exception as e:
        print(f"Ошибка: {e}")
        try:
            await loading_msg.delete()
        except:
            pass
        await message.answer("Произошла небольшая задержка сети. Попробуй еще раз!", reply_markup=clear_keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
