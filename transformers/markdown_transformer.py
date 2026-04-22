import re
from schemas import ArticleSchema
from .transformer_abc import TransformerABC


class MarkdownTransformer(TransformerABC):
    def transform(self, article_list: list[ArticleSchema]) -> str:
        article_md = [
            (
                f'{i}\. [{article.title}]({article.url})'
                f'\n\n{self._clear_reserved(article.summary)}'

            ) for i, article in enumerate(article_list, start=1)
        ]

        full_md = '\n\n\n'.join(article_md)
        return full_md
    
    @staticmethod
    def _clear_reserved(text: str) -> str:
        text = text.replace('.', r'\.')
        text = re.sub(r'[_*\[\]()~`#+\-=|{}!]', '', text)
        return text
