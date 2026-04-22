from abc import ABC, abstractmethod
from schemas import ArticleSchema


class TransformerABC(ABC):
    @abstractmethod
    def transform(self, article_list: list[ArticleSchema]) -> str:
        ...
