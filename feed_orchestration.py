import logging
from schemas import ArticleSchema
from requests_readers import RequestsReaderABC
from parsers import ParserDispatcher
from ai_clients import AIClientABC
from transformers import TransformerABC
from exceptions.parser_exceptions import RequestReaderException, AIClientException, TransformerException

logger = logging.getLogger(__name__)


class FeedOrchestration:
    def __init__(
            self,
            article_count: int,
            request_reader: RequestsReaderABC,
            ai_client: AIClientABC,
            transformer: TransformerABC,
        ):
        self._article_count = article_count
        self._request_reader = request_reader
        self._ai_client = ai_client
        self._transformer = transformer

    async def build_digest(self) -> str:
        logger.info('Digest build started.')

        try:
            requests_list = self._request_reader.read_requests()
        except RequestReaderException:
            logger.exception('Failed to read article requests from config.')
            raise

        try:
            article_list = await ParserDispatcher.parse_articles(article_requests=requests_list)
        except Exception:
            logger.exception('Failed to parse articles.')
            raise

        try:
            article_list = await self._ai_client.get_summary(article_list=article_list)
        except AIClientException:
            logger.exception('AI client failed to summarise articles.')
            raise

        article_list = self._filter_articles(article_list=article_list)

        try:
            article_str = self._transformer.transform(article_list=article_list)
        except TransformerException:
            logger.exception('Transformer failed to format articles.')
            raise

        logger.info('Digest build complete: %d article(s) in output.', len(article_list))
        return article_str

    def _filter_articles(self, article_list: list[ArticleSchema]) -> list[ArticleSchema]:
        list_sorted = sorted(article_list, key=lambda x: x.rating, reverse=True)
        return list_sorted[:self._article_count]
