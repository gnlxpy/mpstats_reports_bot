import traceback
import gspread_asyncio
from config import settings
from google.oauth2.service_account import Credentials


def get_creds():
    """
    Инициализация сервисного аккаунта
    """
    creds = Credentials.from_service_account_file('./gs_key.json', scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return creds


# инициализация асинхронного клиента
gs_client_main = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


async def add_trends_report(path: str, data: list, gs_client=gs_client_main):
    """
    Проверка наличия вкладки, создание если нет, выгрузка данных
    :param path: вкладка
    :param data: данные
    :param gs_client: клиент
    :return: ссылка на выгруженную вкладку
    """
    try:
        # авторизация и открытие документа
        gs = await gs_client.authorize()
        ss = await gs.open_by_key(settings.GS_DOC_KEY)

        # получение списка вкладок
        ws_list = await ss.worksheets()
        ws_list_names = [w.title for w in ws_list]
        # проверка существования вкладки
        if path in ws_list_names:
            print(f'Отчет существует - {path}')
            return None
        # добавление вкладки
        ws = await ss.add_worksheet(path, 100, 12)
        ws_id = ws.id
        ws_url = f'https://docs.google.com/spreadsheets/d/{settings.GS_DOC_KEY}/edit?gid={ws_id}#gid={ws_id}'
        # наполнение вкладки данными
        await ws.append_rows(data, table_range='A1:A1', value_input_option='USER_ENTERED')
        return ws_url
    except Exception as e:
        traceback.print_exc()
        return False


if __name__ == '__main__':
    pass
