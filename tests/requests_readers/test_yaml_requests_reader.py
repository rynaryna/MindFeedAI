import pytest
from pathlib import Path
from requests_readers.yaml_requests_reader import YamlRequestReader
from schemas import SourceEnum
from exceptions.parser_exceptions import RequestReaderException


def write_yaml(tmp_path: Path, content: str) -> str:
    p = tmp_path / 'settings.yaml'
    p.write_text(content, encoding='utf-8')
    return str(p)


def test_reads_valid_yaml_returns_schema_list(tmp_path):
    path = write_yaml(tmp_path, """
sources:
  - source: habr
    article: ai_and_ml
    limit: 10
  - source: devto
    article: python
    limit: 5
""")
    reader = YamlRequestReader(yaml_path=path)
    result = reader.read_requests()
    assert len(result) == 2


def test_extracts_source_article_limit(tmp_path):
    path = write_yaml(tmp_path, """
sources:
  - source: habr
    article: ai_and_ml
    limit: 15
""")
    reader = YamlRequestReader(yaml_path=path)
    result = reader.read_requests()
    request = result[0]
    assert request.source == SourceEnum.HABR
    assert request.article == 'ai_and_ml'
    assert request.limit == 15


def test_file_not_found_raises_request_reader_exception(tmp_path):
    reader = YamlRequestReader(yaml_path=str(tmp_path / 'nonexistent.yaml'))
    with pytest.raises(RequestReaderException):
        reader.read_requests()


def test_malformed_yaml_raises_request_reader_exception(tmp_path):
    path = write_yaml(tmp_path, "sources: [invalid: yaml: {{{")
    reader = YamlRequestReader(yaml_path=path)
    with pytest.raises(RequestReaderException):
        reader.read_requests()


def test_missing_sources_key_raises_exception(tmp_path):
    path = write_yaml(tmp_path, "other_key: value\n")
    reader = YamlRequestReader(yaml_path=path)
    with pytest.raises(RequestReaderException):
        reader.read_requests()


def test_invalid_source_enum_raises_exception(tmp_path):
    path = write_yaml(tmp_path, """
sources:
  - source: unknown_source
    article: test
    limit: 5
""")
    reader = YamlRequestReader(yaml_path=path)
    with pytest.raises(RequestReaderException):
        reader.read_requests()
