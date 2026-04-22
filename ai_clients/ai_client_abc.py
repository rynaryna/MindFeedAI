from abc import ABC, abstractmethod
from schemas import ArticleSchema


class AIClientABC(ABC):
    @abstractmethod
    async def get_summary(self, article_list: list[ArticleSchema]) -> list[ArticleSchema]:
        ...
