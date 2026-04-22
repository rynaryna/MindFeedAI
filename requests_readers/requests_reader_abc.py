from abc import ABC, abstractmethod
from schemas import ArticleRequestSchema


class RequestsReaderABC(ABC):
    @abstractmethod
    def read_requests(self) -> list[ArticleRequestSchema]:
        ...
