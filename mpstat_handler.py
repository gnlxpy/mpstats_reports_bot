import asyncio
import json
import traceback
from datetime import datetime, date, timedelta
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


async def get_raw_trends_data(path: str, d1=None, d2=None, errors_max=3) -> bool | list:
    """
    Получение сырых данных отчета Тренды из Мпстат
    :param path: запрос (категория)
    :param d1: дата от
    :param d2: дата до
    :param errors_max: число ошибок
    :return: список со словарями
    """
    headers = get_headers_mpstat()
    if d1 is None and d2 is None:
        d1, d2 = str(date.today() - timedelta(days=365)), str(date.today() - timedelta(days=1))
    params = {
        'path': path,
        'view': 'itemsInCategory',
        # 'd1': d1,
        # 'd2': d2
    }
    errors = 0
    while True:
        try:
            # асинхронный запрос
            async with httpx.AsyncClient() as client:
                r = await client.get(url='https://mpstats.io/api/wb/get/category/trends',
                                     headers=headers, params=params, timeout=60)
                print('get_raw_trends_data', 'path', path, 'r.status_code', r.status_code)
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


def edit_trends_data(raw_data: list):
    """
    Обработка данных и преобразование в список списков для выгрузки в гугл таблицы
    :param raw_data:
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


async def get_trends(path: str) -> str | bool | None:
    """
    Основная функция загрузки отчета Тренды
    :param path: запрос (категория)
    :return: ссылка на выгруженный отчет / булевое значение
    """
    # Получение сырых данных отчета Тренды из Мпстат
    raw_data = await get_raw_trends_data(path)
    # Обработка данных и преобразование в список списков для выгрузки в гугл таблицы
    gs_data = edit_trends_data(raw_data)
    # выгрузка данных в Гугл таблицы
    status = await add_trends_report(path, gs_data)
    if status is False:
        return False
    elif status is None:
        return None
    return status


if __name__ == '__main__':
    pass
