import pytest
from ai_clients.claude_client.claude_prompt_builder import build_claude_prompt
from schemas import ArticleSchema, SourceEnum


def make_article(title: str, full_text: str) -> ArticleSchema:
    return ArticleSchema(
        source=SourceEnum.HABR,
        title=title,
        url=f'https://habr.com/{title}',
        full_text=full_text,
    )


@pytest.mark.parametrize('articles', [
    [make_article('Single Article', 'Single article text')],
    [
        make_article('First Article', 'First article full text'),
        make_article('Second Article', 'Second article full text'),
    ],
])
def test_prompt_contains_correct_article_data(articles):
    prompt = build_claude_prompt(articles)
    assert isinstance(prompt, str)
    for article in articles:
        assert article.id in prompt
        assert article.title in prompt
        assert article.full_text in prompt
