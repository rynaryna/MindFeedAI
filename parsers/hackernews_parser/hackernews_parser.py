import logging
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from exceptions.parser_exceptions import XMLReaderException
from schemas import ArticleSchema
from ..parser_abc import ParserABC
from ..is_retryable import is_retryable
from .parse_hn_rss import parse_hn_rss
from .extract_generic_text import extract_generic_text

logger = logging.getLogger(__name__)


class HackernewsParser(ParserABC):
    _RSS_URL = 'https://hnrss.org/newest'

    def __init__(self):
        self._timeout = ClientTimeout(total=60)
        self._semaphore_value = 5

    async def parse_article(self, article: str, limit: int = 100) -> list[ArticleSchema]:
        logger.info(f'parse_article(article={article}, limit={limit})')

        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                rss_xml = await self._fetch_rss_feed(session=session, query=article, limit=limit)
                logger.debug(f'XML size: {len(rss_xml)}')

                articles_list = parse_hn_rss(rss_xml)
                logger.debug(f'Articles count: {len(articles_list)}')

                articles_list = await self._hydrate_articles(session=session, articles_list=articles_list)
                return articles_list

        except aiohttp.ClientError as e:
            logger.exception(f'HTTP CLIENT ERROR: {e}', exc_info=True)
            return []

        except XMLReaderException as e:
            logger.exception(f'ERROR READING XML: {e}', exc_info=True)
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
    async def _fetch_rss_feed(self, session: ClientSession, query: str, limit: int = 100) -> str:
        params = {'q': query, 'points': 30, 'count': limit}

        async with session.get(url=self._RSS_URL, params=params) as response:
            response.raise_for_status()
            return await response.text()

    async def _hydrate_articles(self, session: ClientSession, articles_list: list[ArticleSchema]) -> list[ArticleSchema]:
        semaphore = asyncio.Semaphore(self._semaphore_value)
        hydrated_count = 0

        async def _fetch_full_text(article: ArticleSchema) -> ArticleSchema:
            nonlocal hydrated_count
            async with semaphore:
                try:
                    html = await self._fetch_article_html(session=session, url=article.url)
                    article.full_text = extract_generic_text(html)
                    hydrated_count += 1
                except aiohttp.ClientError as e:
                    logger.warning(f'HTTP CLIENT ERROR fetching full text, URL: {article.url}. ERROR: {e}')
                return article

        articles_list = await asyncio.gather(*[_fetch_full_text(a) for a in articles_list])
        logger.info('Hydrated %d/%d articles.', hydrated_count, len(articles_list))
        return list(articles_list)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(is_retryable),
        reraise=True,
    )
    async def _fetch_article_html(self, session: ClientSession, url: str) -> str:
        async with session.get(url=url) as response:
            response.raise_for_status()
            return await response.text()
