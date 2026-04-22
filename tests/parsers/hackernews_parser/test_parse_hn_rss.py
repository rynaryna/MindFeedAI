import pytest
from parsers.hackernews_parser.parse_hn_rss import parse_hn_rss
from schemas import SourceEnum
from exceptions.parser_exceptions import XMLReaderException


VALID_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>HN Article One</title>
      <link>https://example.com/article-1</link>
    </item>
    <item>
      <title>HN Article Two</title>
      <link>https://example.com/article-2</link>
    </item>
  </channel>
</rss>"""


def test_parses_valid_rss_returns_list():
    result = parse_hn_rss(VALID_XML)
    assert len(result) == 2


def test_extracts_title_and_url():
    result = parse_hn_rss(VALID_XML)
    assert result[0].title == "HN Article One"
    assert result[0].url == "https://example.com/article-1"


def test_source_set_to_hackernews():
    result = parse_hn_rss(VALID_XML)
    assert all(a.source == SourceEnum.HACKERNEWS for a in result)


def test_empty_input_raises_xml_exception():
    with pytest.raises(XMLReaderException):
        parse_hn_rss("")


def test_invalid_xml_raises_xml_exception():
    with pytest.raises(XMLReaderException):
        parse_hn_rss("<<< not xml")
