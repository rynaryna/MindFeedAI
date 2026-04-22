import logging
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from schemas import ArticleSchema, SourceEnum
from ..parser_abc import ParserABC
from ..is_retryable import is_retryable

logger = logging.getLogger(__name__)


class DevtoParser(ParserABC):
    _BASE_URL = 'https://dev.to/api'

    def __init__(self):
        self._timeout = ClientTimeout(total=30)
        self._semaphore_value = 10

    async def parse_article(self, article: str, limit: int = 100) -> list[ArticleSchema]:
        logger.info(f'parse_article(article={article}, limit={limit})')

        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                items = await self._fetch_articles_list(session=session, tag=article, limit=limit)
                logger.debug(f'Articles count: {len(items)}')

                articles_list = await self._hydrate_articles(session=session, items=items)
                return articles_list

        except aiohttp.ClientError as e:
            logger.exception(f'HTTP CLIENT ERROR: {e}', exc_info=True)
            return []

        except Exception as e:
            logger.exception(f'UNKNOWN ERROR: {e}', exc_info=True)
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(is_retryable),
        reraise=True,
    )
    async def _fetch_articles_list(self, session: ClientSession, tag: str, limit: int) -> list[dict]:
        url = f'{self._BASE_URL}/articles'
        params = {'tag': tag, 'top': 7, 'per_page': limit}

        async with session.get(url=url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    def _build_article(self, item: dict) -> tuple[ArticleSchema, str]:
        article = ArticleSchema(
            source=SourceEnum.DEVTO,
            title=item.get('title', ''),
            url=item.get('url', ''),
            category_list=item.get('tag_list', []),
        )
        api_url = f"{self._BASE_URL}/articles/{item['id']}"
        return article, api_url

    async def _hydrate_articles(self, session: ClientSession, items: list[dict]) -> list[ArticleSchema]:
        semaphore = asyncio.Semaphore(self._semaphore_value)
        hydrated_count = 0

        async def _fetch_full_text(item: dict) -> ArticleSchema:
            nonlocal hydrated_count
            article, api_url = self._build_article(item)
            async with semaphore:
                try:
                    async with session.get(url=api_url) as response:
                        response.raise_for_status()
                        data = await response.json()
                        article.full_text = data.get('body_markdown') or ''
                        hydrated_count += 1
                except aiohttp.ClientError as e:
                    logger.warning(f'HTTP CLIENT ERROR fetching full text, URL: {api_url}. ERROR: {e}')
                return article

        articles_list = await asyncio.gather(*[_fetch_full_text(item) for item in items])
        logger.info('Hydrated %d/%d articles.', hydrated_count, len(articles_list))
        return list(articles_list)
