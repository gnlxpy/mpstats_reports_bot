from urllib.parse import urlparse, parse_qs


def parse_url(url: str) -> str | bool:
    """
    Проверка ссылки и извлечение категории
    :param url: ссылка
    :return:
    """
    if 'mpstats.io/wb/category/trends?url' not in url or 'https://' not in url or ' ' in url:
        return False
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_url = query_params.get('url')
    if query_url:
        return query_url[0]
    else:
        return False
