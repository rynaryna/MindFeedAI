from .transformer_abc import TransformerABC
from .markdown_transformer import MarkdownTransformer
from config import transformer_types


class TransformerFactory:
    _transformer_types: dict[transformer_types, TransformerABC] = {
        'markdown': MarkdownTransformer
    }

    @classmethod
    def get_transformer(cls, transformer_type: transformer_types) -> TransformerABC:
        if not (transformer := cls._transformer_types.get(transformer_type.lower())):
            raise ValueError()
        
        return transformer()
