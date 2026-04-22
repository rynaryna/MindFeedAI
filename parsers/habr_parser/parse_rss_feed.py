import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from exceptions.parser_exceptions import XMLReaderException
from schemas import ArticleSchema, SourceEnum


def _clear_cdata(text_raw: str) -> str:
    text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text_raw, flags=re.DOTALL)
    return text


def parse_rss_feed(article_list_xml: str) -> list[ArticleSchema]:
    if not isinstance(article_list_xml, str) or article_list_xml == '':
        raise XMLReaderException(f'Incorrect article_list_xml value: {type(article_list_xml)}')
    
    articles_list = []
    try:
        root  = ET.fromstring(article_list_xml)

    except ParseError as e:
        raise XMLReaderException(f'Error parsing XML') from e

    channel = root.find('channel')
    if channel is None:
        return []

    for item in channel.findall('item'):
        title_el = item.find('title')
        title = _clear_cdata(title_el.text or '') if title_el is not None else ''

        url_el = item.find('link')
        if url_el is None or url_el.text is None:
            continue

        url = url_el.text

        category_list_el = item.findall('category')
        category_list = [_clear_cdata(x.text) for x in category_list_el if x.text is not None]

        articles_list.append(
            ArticleSchema(
                source=SourceEnum.HABR,
                title=title,
                url=url,
                category_list=category_list
            )
        )

    return articles_list    
