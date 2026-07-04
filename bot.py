import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
NORD_API_KEY = os.getenv("NORD_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = OpenAI(
    base_url="https://nordrouter.com/v1",
    api_key=NORD_API_KEY,
)

user_models = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Claude")],
        [KeyboardButton(text="GPT-5.5")],
        [KeyboardButton(text="DeepSeek")],
        [KeyboardButton(text="Image")]
    ],
    resize_keyboard=True
)

MODELS = {
    "Claude": "anthropic/claude-sonnet-4.6",
    "GPT-5.5": "openai/gpt-5.5",
    "DeepSeek": "deepseek/deepseek-v4-pro"
}

@dp.message(CommandStart())
async def start(message: Message):
    user_models[message.from_user.id] = (
        "anthropic/claude-sonnet-4.6"
    )

    await message.answer(
        "AI бот готов.\nВыберите модель:",
        reply_markup=keyboard
    )

@dp.message(F.text.in_(["Claude", "GPT-5.5", "DeepSeek"]))
async def change_model(message: Message):
    model = MODELS[message.text]

    user_models[message.from_user.id] = model

    await message.answer(
        f"Модель переключена:\n{model}"
    )

@dp.message(F.text == "Image")
async def image_info(message: Message):
    await message.answer(
        "Напишите:\nнарисуй кота в киберпанке"
    )

@dp.message()
async def ai_chat(message: Message):

    text = message.text

    if text.startswith("/"):
        return

    # Генерация изображений
    if text.lower().startswith("нарисуй"):

        try:
            result = client.images.generate(
                model="openai/gpt-image-2",
                prompt=text,
                size="1024x1024"
            )

            image_base64 = result.data[0].b64_json

            import base64

            with open("generated.png", "wb") as f:
                f.write(base64.b64decode(image_base64))

            await message.answer_photo(
                photo=open("generated.png", "rb")
            )

        except Exception as e:
            await message.answer(str(e))

        return

    model = user_models.get(
        message.from_user.id,
        "anthropic/claude-sonnet-4.6"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        answer = response.choices[0].message.content

        if not answer:
            answer = "Пустой ответ модели."

        await message.answer(answer)

    except Exception as e:
        await message.answer(
            f"Ошибка:\n{str(e)}"
        )

async def main():
    print("Bot started")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
