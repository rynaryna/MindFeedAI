import logging
from schemas import ArticleSchema, ArticleRequestSchema, SourceEnum
from .parser_abc import ParserABC
from .habr_parser import HabrParser
from .devto_parser import DevtoParser
from .hackernews_parser import HackernewsParser

logger = logging.getLogger(__name__)


class ParserDispatcher:
    _parser_map: dict[SourceEnum, ParserABC] = {
        SourceEnum.HABR: HabrParser(),
        SourceEnum.DEVTO: DevtoParser(),
        SourceEnum.HACKERNEWS: HackernewsParser(),
    }

    @classmethod
    async def parse_articles(cls, article_requests: list[ArticleRequestSchema]) -> list[ArticleSchema]:
        logger.info('Dispatching %d parse request(s).', len(article_requests))
        result = []

        for request in article_requests:
            if not (parser := cls._parser_map.get(request.source)):
                logger.warning('No parser registered for source %r — skipping.', request.source)
                continue

            _result = await parser.parse_article(article=request.article, limit=request.limit)
            result.extend(_result)

        logger.info('Parsing complete: %d article(s) total.', len(result))
        return result
