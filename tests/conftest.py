import pytest
from schemas import ArticleSchema, ArticleRequestSchema, SourceEnum


@pytest.fixture
def habr_article():
    return ArticleSchema(
        source=SourceEnum.HABR,
        title="Test Habr Article",
        url="https://habr.com/ru/articles/test",
        full_text="Some article text",
        summary="A brief summary",
        rating=75,
    )


@pytest.fixture
def hn_article():
    return ArticleSchema(
        source=SourceEnum.HACKERNEWS,
        title="HN Test Article",
        url="https://example.com/hn-article",
        full_text="HN article text",
    )


@pytest.fixture
def devto_article():
    return ArticleSchema(
        source=SourceEnum.DEVTO,
        title="Dev.to Test Article",
        url="https://dev.to/test/article",
        full_text="Dev.to markdown text",
    )


@pytest.fixture
def habr_request():
    return ArticleRequestSchema(source=SourceEnum.HABR, article="ai_and_ml", limit=5)
