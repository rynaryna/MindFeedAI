from .requests_reader_abc import RequestsReaderABC
from .yaml_requests_reader import YamlRequestReader
from config import request_reader_types


class RequestReaderFactory:
    _reader_types: dict[request_reader_types, RequestsReaderABC] = {
        'yml': YamlRequestReader
    }

    @classmethod
    def get_reader(cls, reader_type: request_reader_types, **kwargs) -> RequestsReaderABC:
        if not (reader := cls._reader_types.get(reader_type.lower())):
            raise ValueError()
        
        return reader(**kwargs)
