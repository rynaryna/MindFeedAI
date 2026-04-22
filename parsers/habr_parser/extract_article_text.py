import re
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from exceptions.parser_exceptions import HTMLReaderException


def extract_article_text(article_html: str) -> str:
    if not isinstance(article_html, str) or article_html == '':
        raise HTMLReaderException(f'Incorrect article_html value: {type(article_html)}')

    soup = BeautifulSoup(article_html, 'html.parser')

    body = soup.find('div', class_='article-formatted-body')
    if body is None:
        return ''

    for figure in body.find_all('figure'):
        figure.decompose()

    try:
        article_full_text = md(
            str(body),
            heading_style='ATX',
            strip=["a", "img", "table", "ul", "ol", "li", "blockquote", "code", "pre"]
        )

    except Exception as e:
        raise HTMLReaderException('Error formatting HTML as Markdown') from e

    article_full_text = re.sub(r'\n{2,}', r'\n', article_full_text).strip()
    return article_full_text
