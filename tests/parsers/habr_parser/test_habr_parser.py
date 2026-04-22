import aiohttp
import pytest
from unittest.mock import AsyncMock, patch
from parsers.habr_parser.habr_parser import HabrParser


MINIMAL_RSS = """<rss><channel>
  <item>
    <title><![CDATA[Article A]]></title>
    <link>https://habr.com/articles/1</link>
  </item>
</channel></rss>"""

ARTICLE_HTML = '<html><body><div class="article-formatted-body"><p>Full text here</p></div></body></html>'


@pytest.fixture
def parser():
    return HabrParser()


def test_semaphore_value_is_10(parser):
    assert parser._semaphore_value == 10


async def test_parse_article_returns_article_list(parser):
    with (
        patch.object(parser, '_fetch_rss_feed', new=AsyncMock(return_value=MINIMAL_RSS)),
        patch.object(parser, '_fetch_article_html', new=AsyncMock(return_value=ARTICLE_HTML)),
    ):
        result = await parser.parse_article(article='ai_and_ml', limit=5)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].title == 'Article A'


async def test_hydration_sets_full_text(parser):
    with (
        patch.object(parser, '_fetch_rss_feed', new=AsyncMock(return_value=MINIMAL_RSS)),
        patch.object(parser, '_fetch_article_html', new=AsyncMock(return_value=ARTICLE_HTML)),
    ):
        result = await parser.parse_article(article='ai_and_ml', limit=5)

    assert result[0].full_text != ''
    assert 'Full text here' in result[0].full_text


async def test_empty_full_text_on_hydration_failure(parser):
    with (
        patch.object(parser, '_fetch_rss_feed', new=AsyncMock(return_value=MINIMAL_RSS)),
        patch.object(parser, '_fetch_article_html', new=AsyncMock(side_effect=aiohttp.ClientError())),
    ):
        result = await parser.parse_article(article='ai_and_ml', limit=5)

    assert len(result) == 1
    assert result[0].full_text == ''


async def test_http_error_on_rss_returns_empty_list(parser):
    with patch.object(parser, '_fetch_rss_feed', new=AsyncMock(side_effect=aiohttp.ClientError())):
        result = await parser.parse_article(article='ai_and_ml', limit=5)

    assert result == []
