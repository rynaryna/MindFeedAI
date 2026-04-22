from abc import ABC, abstractmethod
from schemas import ArticleSchema


class ParserABC(ABC):
    @abstractmethod
    async def parse_article(self, article: str, limit: int) -> list[ArticleSchema]:
        ...
