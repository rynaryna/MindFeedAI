from .transformer_abc import TransformerABC
from schemas import ArticleSchema


class MarkdownTransformer(TransformerABC):
    def transform(self, article_list: list[ArticleSchema]) -> str:
        article_md = [
            (
                f'{i}. [{article.title}]({article.url})'
                f'\n\n{article.summary}'

            ) for i, article in enumerate(article_list, start=1)
        ]

        full_md = '\n\n\n'.join(article_md)
        return full_md
