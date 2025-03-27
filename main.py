import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from common import parse_url, ReportType, ErrorsMsg
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
                         "Я могу скачивать отчет Мпстатс в гугл таблицы (Тренды)\n"
                         "Пришли ссылку как в формате ниже и получи готовый отчет через несколько секунд:\n"
                         "По предмету https://mpstats.io/wb/subject/trends...\n"
                         "По категории https://mpstats.io/wb/category/trends...\n"
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
    report_type, query_url = parse_url(text)
    if report_type is False:
        await message.answer(ErrorsMsg.URL.value)
        return
    await message.answer(f'🚀Начат отчет {report_type.value["name"]}')
    # формируем отчет
    ws_url = await get_trends(report_type.name, report_type.value['url'], query_url)
    # отправляем ответ
    if ws_url is False:
        await message.answer(ErrorsMsg.OTHER.value)
    elif ws_url is None:
        await message.answer(ErrorsMsg.REPEAT.value)
    else:
        await message.answer(f'{report_type.value['msg']}\"{query_url}\" обработан и выгружен по ссылке: {ws_url}')


async def main():
    print('Тг-бот запущен!')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
