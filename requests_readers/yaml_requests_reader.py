import logging
import yaml
from pydantic import ValidationError
from schemas import ArticleRequestSchema
from exceptions.parser_exceptions import RequestReaderException
from .requests_reader_abc import RequestsReaderABC

logger = logging.getLogger(__name__)


class YamlRequestReader(RequestsReaderABC):
    def __init__(self, yaml_path: str):
        self._yaml_path = yaml_path

    def read_requests(self) -> list[ArticleRequestSchema]:
        try:
            with open(self._yaml_path, 'r', encoding='utf-8') as fp:
                yaml_data = yaml.safe_load(fp)
        except FileNotFoundError:
            raise RequestReaderException(f'Config file not found: {self._yaml_path}')
        except OSError as e:
            raise RequestReaderException(f'Cannot read config file: {self._yaml_path}') from e
        except yaml.YAMLError as e:
            raise RequestReaderException(f'Invalid YAML in config file: {self._yaml_path}') from e

        try:
            sources = yaml_data['sources']
        except (KeyError, TypeError):
            raise RequestReaderException(f'Missing "sources" key in config file: {self._yaml_path}')

        requests = []
        for i, source in enumerate(sources):
            try:
                request = ArticleRequestSchema(
                    source=source['source'],
                    article=source['article'],
                    limit=source['limit']
                )
            except KeyError as e:
                raise RequestReaderException(f'Missing field {e} in sources[{i}]') from e
            except ValidationError as e:
                raise RequestReaderException(f'Invalid value in sources[{i}]: {e}') from e
            requests.append(request)

        logger.info('Loaded %d article request(s) from %s.', len(requests), self._yaml_path)
        return requests
