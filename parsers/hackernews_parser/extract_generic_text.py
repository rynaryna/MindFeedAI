import re
from bs4 import BeautifulSoup


def extract_generic_text(html: str) -> str:
    if not isinstance(html, str) or html == '':
        return ''

    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()

    paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]
    text = '\n'.join(p for p in paragraphs if p)
    text = re.sub(r'\n{2,}', '\n', text).strip()
    return text
