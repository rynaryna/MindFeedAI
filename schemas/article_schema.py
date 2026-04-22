import hashlib
from pydantic import BaseModel, computed_field
from enum import StrEnum


class SourceEnum(StrEnum):
    HABR = 'habr'


class ArticleRequestSchema(BaseModel):
    source: SourceEnum
    article: str
    limit: int


class ArticleSchema(BaseModel):
    source: SourceEnum
    title: str
    url: str
    full_text: str = ''
    category_list: list[str] = []
    summary: str = ''
    rating: int = 0

    @computed_field
    @property
    def id(self) -> str:
        return hashlib.md5(f"{self.source}:{self.title}".encode()).hexdigest()
