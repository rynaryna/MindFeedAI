import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from parsers.devto_parser.devto_parser import DevtoParser
from schemas import ArticleSchema, SourceEnum


DEVTO_ITEMS = [
    {
        'id': 123,
        'title': 'Dev.to Article',
        'url': 'https://dev.to/user/article',
        'tag_list': ['python', 'ai'],
    }
]


@pytest.fixture
def parser():
    return DevtoParser()


async def test_parse_article_returns_article_list(parser):
    article = ArticleSchema(
        source=SourceEnum.DEVTO,
        title='Dev.to Article',
        url='https://dev.to/user/article',
        full_text='Some markdown',
    )
    with (
        patch.object(parser, '_fetch_articles_list', new=AsyncMock(return_value=DEVTO_ITEMS)),
        patch.object(parser, '_hydrate_articles', new=AsyncMock(return_value=[article])),
    ):
        result = await parser.parse_article(article='python', limit=5)

    assert len(result) == 1
    assert result[0].title == 'Dev.to Article'


def test_build_article_extracts_title_url_tags(parser):
    item = {
        'id': 42,
        'title': 'My Article',
        'url': 'https://dev.to/user/my-article',
        'tag_list': ['python', 'tutorial'],
    }
    article, api_url = parser._build_article(item)

    assert article.title == 'My Article'
    assert article.url == 'https://dev.to/user/my-article'
    assert article.category_list == ['python', 'tutorial']
    assert '42' in api_url


def test_source_set_to_devto(parser):
    item = {'id': 1, 'title': 'Test', 'url': 'https://dev.to/test', 'tag_list': []}
    article, _ = parser._build_article(item)
    assert article.source == SourceEnum.DEVTO


async def test_hydration_uses_body_markdown(parser):
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={'body_markdown': 'Some markdown text'})
    mock_response.raise_for_status = MagicMock()
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_response)

    items = [{'id': 99, 'title': 'Test', 'url': 'https://dev.to/test', 'tag_list': []}]
    result = await parser._hydrate_articles(session=mock_session, items=items)

    assert len(result) == 1
    assert result[0].full_text == 'Some markdown text'


async def test_http_error_returns_empty_list(parser):
    import aiohttp
    with patch.object(parser, '_fetch_articles_list', new=AsyncMock(side_effect=aiohttp.ClientError())):
        result = await parser.parse_article(article='python', limit=5)

    assert result == []
