import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from exceptions.parser_exceptions import XMLReaderException
from schemas import ArticleSchema, SourceEnum


def parse_hn_rss(rss_xml: str) -> list[ArticleSchema]:
    if not isinstance(rss_xml, str) or rss_xml == '':
        raise XMLReaderException(f'Incorrect rss_xml value: {type(rss_xml)}')

    try:
        root = ET.fromstring(rss_xml)
    except ParseError as e:
        raise XMLReaderException('Error parsing HN RSS XML') from e

    channel = root.find('channel')
    if channel is None:
        return []

    articles = []
    for item in channel.findall('item'):
        title_el = item.find('title')
        title = title_el.text or '' if title_el is not None else ''

        link_el = item.find('link')
        if link_el is None or link_el.text is None:
            continue

        articles.append(ArticleSchema(
            source=SourceEnum.HACKERNEWS,
            title=title,
            url=link_el.text,
        ))

    return articles
