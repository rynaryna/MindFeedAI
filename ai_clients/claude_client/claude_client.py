import logging
from schemas import ArticleSchema
from exceptions.parser_exceptions import AIClientException
from ..ai_client_abc import AIClientABC
from .claude_prompt_builder import build_claude_prompt
from .claude_interface import invoke_claude_cli
from .claude_response_parser import parse_claude_response

logger = logging.getLogger(__name__)


class ClaudeClient(AIClientABC):
    def __init__(self, articles_per_call: int = 5):
        self._articles_per_call = articles_per_call

    async def get_summary(self, article_list: list[ArticleSchema]) -> list[ArticleSchema]:
        batch_count = -(-len(article_list) // self._articles_per_call)  # ceiling division
        logger.info('Starting summarisation: %d article(s) in %d batch(es).', len(article_list), batch_count)
        result_articles = []

        for i in range(0, len(article_list), self._articles_per_call):
            current_articles = article_list[i:i + self._articles_per_call]
            prompt = build_claude_prompt(current_articles)
            try:
                response = await invoke_claude_cli(prompt=prompt)
            except AIClientException:
                logger.exception(f'Claude CLI failed for batch starting at index {i}. Skipping batch.')
                continue

            result = parse_claude_response(response=response, article_list=current_articles)
            result_articles.extend(result)

        logger.info('Summarisation complete: %d/%d article(s) processed.', len(result_articles), len(article_list))
        return result_articles
