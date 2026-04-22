import pytest
from transformers.markdown_transformer import MarkdownTransformer
from schemas import ArticleSchema, SourceEnum


def make_article(title: str, url: str, summary: str) -> ArticleSchema:
    return ArticleSchema(
        source=SourceEnum.HABR,
        title=title,
        url=url,
        summary=summary,
    )


@pytest.fixture
def transformer():
    return MarkdownTransformer()


def test_formats_single_article_correctly(transformer):
    article = make_article('My Title', 'https://example.com', 'My summary text')
    result = transformer.transform([article])
    assert result == '1. [My Title](https://example.com)\n\nMy summary text'


def test_summary_included_in_output(transformer):
    article = make_article('Title', 'https://x.com', 'This is the summary')
    result = transformer.transform([article])
    assert 'This is the summary' in result


def test_empty_list_returns_empty_string(transformer):
    result = transformer.transform([])
    assert result == ''


def test_multiple_articles_numbered_sequentially(transformer):
    articles = [
        make_article('First', 'https://a.com', 'A'),
        make_article('Second', 'https://b.com', 'B'),
        make_article('Third', 'https://c.com', 'C'),
    ]
    result = transformer.transform(articles)
    assert '1.' in result
    assert '2.' in result
    assert '3.' in result
