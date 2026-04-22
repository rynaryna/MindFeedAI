import aiohttp
import pytest
from unittest.mock import AsyncMock, patch
from parsers.hackernews_parser.hackernews_parser import HackernewsParser


MINIMAL_RSS = """<rss><channel>
  <item>
    <title>HN Article</title>
    <link>https://example.com/hn-1</link>
  </item>
</channel></rss>"""

ARTICLE_HTML = "<html><body><p>Full article content here</p></body></html>"


@pytest.fixture
def parser():
    return HackernewsParser()


def test_semaphore_value_is_5(parser):
    assert parser._semaphore_value == 5


async def test_parse_article_returns_article_list(parser):
    with (
        patch.object(parser, '_fetch_rss_feed', new=AsyncMock(return_value=MINIMAL_RSS)),
        patch.object(parser, '_fetch_article_html', new=AsyncMock(return_value=ARTICLE_HTML)),
    ):
        result = await parser.parse_article(article='python', limit=10)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].title == 'HN Article'


async def test_hydration_sets_full_text(parser):
    with (
        patch.object(parser, '_fetch_rss_feed', new=AsyncMock(return_value=MINIMAL_RSS)),
        patch.object(parser, '_fetch_article_html', new=AsyncMock(return_value=ARTICLE_HTML)),
    ):
        result = await parser.parse_article(article='python', limit=10)

    assert result[0].full_text != ''
    assert 'Full article content here' in result[0].full_text


async def test_failed_hydration_keeps_empty_full_text(parser):
    with (
        patch.object(parser, '_fetch_rss_feed', new=AsyncMock(return_value=MINIMAL_RSS)),
        patch.object(parser, '_fetch_article_html', new=AsyncMock(side_effect=aiohttp.ClientError())),
    ):
        result = await parser.parse_article(article='python', limit=10)

    assert len(result) == 1
    assert result[0].full_text == ''


async def test_http_error_on_rss_returns_empty_list(parser):
    with patch.object(parser, '_fetch_rss_feed', new=AsyncMock(side_effect=aiohttp.ClientError())):
        result = await parser.parse_article(article='python', limit=10)

    assert result == []
