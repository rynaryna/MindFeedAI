import json
import pytest
from ai_clients.claude_client.claude_response_parser import parse_claude_response
from schemas import ArticleSchema, SourceEnum


def make_article(title: str) -> ArticleSchema:
    return ArticleSchema(source=SourceEnum.HABR, title=title, url=f'https://habr.com/{title}')


def make_response(data: list[dict]) -> str:
    payload = json.dumps({'data': data})
    return f'```json\n{payload}\n```'


def test_parses_valid_json_block():
    article = make_article('Test Article')
    response = make_response([{'id': article.id, 'summary': 'Great article', 'rating': 90}])
    result = parse_claude_response(response=response, article_list=[article])
    assert len(result) == 1


def test_sets_summary_on_matched_article():
    article = make_article('Test Article')
    response = make_response([{'id': article.id, 'summary': 'Great article', 'rating': 90}])
    result = parse_claude_response(response=response, article_list=[article])
    assert result[0].summary == 'Great article'


def test_sets_rating_on_matched_article():
    article = make_article('Test Article')
    response = make_response([{'id': article.id, 'summary': 'Great article', 'rating': 90}])
    result = parse_claude_response(response=response, article_list=[article])
    assert result[0].rating == 90


def test_returns_empty_list_when_no_json_block():
    article = make_article('Test Article')
    result = parse_claude_response(response='No JSON here at all.', article_list=[article])
    assert result == []


def test_returns_empty_list_on_invalid_json():
    article = make_article('Test Article')
    response = '```json\n{invalid json!!!\n```'
    result = parse_claude_response(response=response, article_list=[article])
    assert result == []


def test_ignores_unknown_article_ids():
    article = make_article('Test Article')
    response = make_response([{'id': 'unknown-id-xyz', 'summary': 'Oops', 'rating': 50}])
    result = parse_claude_response(response=response, article_list=[article])
    assert result == []


def test_multiple_articles_matched_correctly():
    a1 = make_article('Article One')
    a2 = make_article('Article Two')
    response = make_response([
        {'id': a1.id, 'summary': 'Summary one', 'rating': 80},
        {'id': a2.id, 'summary': 'Summary two', 'rating': 60},
    ])
    result = parse_claude_response(response=response, article_list=[a1, a2])
    assert len(result) == 2
    by_title = {a.title: a for a in result}
    assert by_title['Article One'].summary == 'Summary one'
    assert by_title['Article Two'].rating == 60
