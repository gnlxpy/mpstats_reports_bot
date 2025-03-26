import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from common import parse_url
from config import settings
from mpstat_handler import get_trends


# Настраиваем логирование
bot = Bot(token=settings.TG_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    """
    Приветственное сообщение
    """
    await message.answer("Привет 👋 \n"
                         "Я могу скачивать отчет Мпстатс в гугл таблицы (По категории - Тренды)\n"
                         "Пришли ссылку как в формате ниже и получи готовый отчет через несколько секунд:\n"
                         "https://mpstats.io/wb/category/trends?url=%D0%96%D0%B5%D0%BD%D1%89%D0%B8%D0%BD%D0%B0%D0%BC%2F%D0%91%D0%BE%D0%BB%D1%8C%D1%88%D0%B8%D0%B5%20%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%80%D1%8B%2F%D0%94%D0%B6%D0%B8%D0%BD%D1%81%D1%8B,%20%D0%B1%D1%80%D1%8E%D0%BA%D0%B8%2F%D0%91%D1%80%D1%8E%D0%BA%D0%B8&d1=23.02.2025&d2=24.03.2025\n"
                         "Приступим? 🤖")


@dp.message()
async def handle_message(message: Message):
    """
    Обработчик всех входящих сообщений
    """
    # определяем id и текст юзера
    # tg_id = message.from_user.id
    text = message.text
    # проверяем ссылку
    query_url = parse_url(text)
    if not query_url:
        await message.answer('😡Неверный формат ссылки ')
        return
    await message.answer('🚀Начат сбор данных')
    # формируем отчет
    ws_url = await get_trends(query_url)
    # отправляем ответ
    if ws_url is False:
        await message.answer('😥Извините.. Произошла ошибка обработки отчета')
    elif ws_url is None:
        await message.answer('😥Данный отчет уже существует')
    else:
        await message.answer(f'✅Запрос: \"{query_url}\" обработан и выгружен по ссылке: {ws_url}')


async def main():
    print('Тг-бот запущен!')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
