import pytest
from unittest.mock import AsyncMock, patch
from parsers.parser_dispatcher import ParserDispatcher
from schemas import ArticleSchema, ArticleRequestSchema, SourceEnum


def make_article(source: SourceEnum, title: str) -> ArticleSchema:
    return ArticleSchema(source=source, title=title, url=f'https://example.com/{title}')


async def test_routes_habr_to_habr_parser():
    request = ArticleRequestSchema(source=SourceEnum.HABR, article='ai_and_ml', limit=5)
    expected = [make_article(SourceEnum.HABR, 'Habr Article')]

    mock_habr = AsyncMock(return_value=expected)
    with patch.dict(ParserDispatcher._parser_map, {SourceEnum.HABR: AsyncMock(parse_article=mock_habr)}):
        ParserDispatcher._parser_map[SourceEnum.HABR].parse_article = mock_habr
        result = await ParserDispatcher.parse_articles([request])

    assert result == expected


async def test_routes_devto_to_devto_parser():
    request = ArticleRequestSchema(source=SourceEnum.DEVTO, article='python', limit=5)
    expected = [make_article(SourceEnum.DEVTO, 'Devto Article')]

    mock_parser = AsyncMock()
    mock_parser.parse_article = AsyncMock(return_value=expected)
    with patch.dict(ParserDispatcher._parser_map, {SourceEnum.DEVTO: mock_parser}):
        result = await ParserDispatcher.parse_articles([request])

    assert result == expected


async def test_routes_hackernews_to_hackernews_parser():
    request = ArticleRequestSchema(source=SourceEnum.HACKERNEWS, article='python', limit=5)
    expected = [make_article(SourceEnum.HACKERNEWS, 'HN Article')]

    mock_parser = AsyncMock()
    mock_parser.parse_article = AsyncMock(return_value=expected)
    with patch.dict(ParserDispatcher._parser_map, {SourceEnum.HACKERNEWS: mock_parser}):
        result = await ParserDispatcher.parse_articles([request])

    assert result == expected


async def test_returns_combined_results_from_multiple_sources():
    habr_article = make_article(SourceEnum.HABR, 'Habr Article')
    hn_article = make_article(SourceEnum.HACKERNEWS, 'HN Article')

    mock_habr = AsyncMock()
    mock_habr.parse_article = AsyncMock(return_value=[habr_article])
    mock_hn = AsyncMock()
    mock_hn.parse_article = AsyncMock(return_value=[hn_article])

    requests = [
        ArticleRequestSchema(source=SourceEnum.HABR, article='ai_and_ml', limit=5),
        ArticleRequestSchema(source=SourceEnum.HACKERNEWS, article='python', limit=5),
    ]
    with patch.dict(ParserDispatcher._parser_map, {
        SourceEnum.HABR: mock_habr,
        SourceEnum.HACKERNEWS: mock_hn,
    }):
        result = await ParserDispatcher.parse_articles(requests)

    assert len(result) == 2
    titles = {a.title for a in result}
    assert 'Habr Article' in titles
    assert 'HN Article' in titles
