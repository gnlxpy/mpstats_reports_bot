import traceback
from enum import Enum
from urllib.parse import urlparse, parse_qs


class ReportType(Enum):
    # отчет по категории
    CAT = {
        'name': 'Тренды по Категории',
        'url': 'https://mpstats.io/api/wb/get/category/trends',
        'msg': '✅Отчет по категории запросу: '
    }
    # отчет по предмету
    SUBJ = {
        'name': 'Тренды по Предметам',
        'url': 'https://mpstats.io/api/wb/get/subject/trends',
        'msg': '✅Отчет по предмету: id '
    }


class ErrorsMsg(Enum):
    URL = '😡Неверный формат ссылки '
    OTHER = '😥Извините.. Произошла ошибка обработки отчета'
    REPEAT = '😥Данный отчет уже существует'


def parse_url(url: str) -> tuple[ReportType, str] | tuple[bool, None]:
    """
    Проверка ссылки и извлечение категории
    :param url: ссылка
    :return:
    """
    try:
        if 'mpstats.io/wb/' not in url or 'https://' not in url or ' ' in url:
            return False, None
        query_url = None
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        # обнаружен отчет по категории
        if 'mpstats.io/wb/category/trends' in url:
            query_url = query_params.get('url')
        # обнаружен отчет по предмету
        if 'mpstats.io/wb/subject/trends' in url:
            query_url = query_params.get('id')
        if query_url:
            return ReportType.SUBJ, query_url[0]
        return False, None
    except Exception:
        traceback.print_exc()
        return False, None


if __name__ == '__main__':
    pass
