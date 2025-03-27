import asyncio
import json
import traceback
import httpx
from config import settings
import pandas as pd
import numpy as np


from gs_handler import add_trends_report


def get_headers_mpstat():
    """
    Создание словаря с заголовками для отправки запросов к апи Мпстат
    :return: словарь с заголовками
    """
    headers = {
        "X-Mpstats-TOKEN": f"{settings.MPSTAT_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return headers


async def get_mpstat_report(url: str, params: dict, errors_max=3) -> bool | list:
    """
    Получение сырых данных отчета из Мпстат
    :param path: запрос (категория)
    :param errors_max: число ошибок
    :return: список со словарями
    """
    headers = get_headers_mpstat()
    errors = 0
    while True:
        try:
            # асинхронный запрос
            async with httpx.AsyncClient() as client:
                r = await client.get(url=url,
                                     headers=headers, params=params, timeout=60)
                print(f'GET path {url} r.status_code {r.status_code}')
            # проверка кодов ошибок
            if r.status_code == 200:
                try:
                    # преобразование в объект пайтон
                    data = json.loads(r.text)
                    if len(data) == 0:
                        return False
                    return data
                except Exception:
                    return False
            if r.status_code in [429, 500]:
                errors += 1
                if errors >= errors_max:
                    return False
                await asyncio.sleep(10)
                continue
            else:
                return False
        except Exception:
            traceback.print_exc()
            errors += 1
            if errors >= errors_max:
                return False
            continue


def edit_trends(raw_data: list):
    """
    Обработка данных и преобразование в список списков для выгрузки в гугл таблицы
    :param raw_data: сырые данные от АПИ
    :return:
    """
    # словарь для наполнения
    main_dict = {'Месяц': [], 'Продажи': [], 'Выручка': [], 'Товары': [], 'Товары с продажами': [], 'Бренды': [],
                 'Бренды с продажами': [], 'Продавцы': [], 'Продавцы с продажами': [], 'Выручка на товар': [],
                 'Средний чек': []}
    try:
        # перебор всего списка с данными
        for row in raw_data:
            main_dict['Месяц'].append(row.get('date'))
            main_dict['Товары'].append(row.get('items'))
            main_dict['Товары с продажами'].append(row.get('items_with_sells'))
            main_dict['Бренды'].append(row.get('brands'))
            main_dict['Бренды с продажами'].append(row.get('brands_with_sells'))
            main_dict['Продавцы'].append(row.get('sellers'))
            main_dict['Продавцы с продажами'].append(row.get('sellers_with_sells'))
            main_dict['Продажи'].append(row.get('sales'))
            main_dict['Выручка'].append(row.get('revenue'))
            main_dict['Выручка на товар'].append(row.get('product_revenue'))
            main_dict['Средний чек'].append(row.get('average_order_value'))
        # загрузка словаря в датафрейм
        df = pd.DataFrame(main_dict)
        if len(df) == 0:
            return False
        # сортировка по датам
        df['Месяц'] = pd.to_datetime(df['Месяц'], format='%Y-%m-%d')
        df_filtered = df.sort_values(by='Месяц', ascending=False)
        df_filtered['Месяц'] = df_filtered['Месяц'].dt.strftime('%d.%m.%Y')
        # прикрепление заголовков и экспорт в виде списка
        gs_data = [df.keys().tolist()] + df_filtered.replace(np.nan, None).values.tolist()
    except Exception:
        traceback.print_exc()
        return False
    return gs_data


async def get_trends(type_report_name: str, url: str, path: str) -> str | bool | None:
    """
    Основная функция загрузки отчета Тренды
    :param path: запрос (категория)
    :return: ссылка на выгруженный отчет / булевое значение
    """
    # подготовка заголовков
    params = {'path': path}
    if type_report_name == 'CAT':
        params['view'] = 'itemsInCategory'

    # Получение сырых данных отчета Тренды из Мпстат
    raw_data = await get_mpstat_report(url, params)
    # Обработка данных и преобразование в список списков для выгрузки в гугл таблицы
    gs_data = edit_trends(raw_data)
    if not gs_data:
        return False
    if type_report_name == 'CAT':
        worksheet = path
    else:
        worksheet = f'id предмета {path}'

    # выгрузка данных в Гугл таблицы
    status = await add_trends_report(worksheet, gs_data)

    return status


if __name__ == '__main__':
    pass
