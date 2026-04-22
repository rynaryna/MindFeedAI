import re
import json
import logging
from schemas import ArticleSchema

logger = logging.getLogger(__name__)


def parse_claude_response(response: str, article_list: list[ArticleSchema]) -> list[ArticleSchema]:
    articles_by_id = {article.id: article for article in article_list}
    result_articles = []

    pattern = r'```json\s*(\{.*?\})\s*```'
    match = re.search(pattern, response, re.DOTALL)
    if not match:
        logger.warning('Claude response does not contain a JSON block.')
        return result_articles

    try:
        data: dict = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        logger.exception(f'Failed to parse JSON from Claude response: {e}')
        return result_articles

    for raw_article in data.get('data', []):
        article_id = raw_article.get('id')
        if not article_id:
            logger.warning('Skipping Claude response entry with missing "id".')
            continue

        article = articles_by_id.get(article_id)
        if not article:
            logger.warning(f'Claude returned unknown article id: {article_id!r}')
            continue

        article.summary = raw_article.get('summary', '')
        article.rating = raw_article.get('rating', 0)
        result_articles.append(article)

    return result_articles
