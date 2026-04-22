import pytest
from parsers.habr_parser.parse_rss_feed import parse_rss_feed
from schemas import SourceEnum
from exceptions.parser_exceptions import XMLReaderException


VALID_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title><![CDATA[Test Article One]]></title>
      <link>https://habr.com/articles/1</link>
      <category><![CDATA[AI]]></category>
      <category><![CDATA[ML]]></category>
    </item>
    <item>
      <title><![CDATA[Test Article Two]]></title>
      <link>https://habr.com/articles/2</link>
      <category><![CDATA[Python]]></category>
    </item>
  </channel>
</rss>"""


def test_parses_valid_rss_returns_article_list():
    result = parse_rss_feed(VALID_XML)
    assert len(result) == 2


def test_extracts_title_url_categories():
    result = parse_rss_feed(VALID_XML)
    first = result[0]
    assert first.title == "Test Article One"
    assert first.url == "https://habr.com/articles/1"
    assert first.category_list == ["AI", "ML"]


def test_cdata_stripped_from_title():
    xml = """<rss><channel><item>
      <title><![CDATA[My CDATA Title]]></title>
      <link>https://habr.com/1</link>
    </item></channel></rss>"""
    result = parse_rss_feed(xml)
    assert result[0].title == "My CDATA Title"


def test_source_set_to_habr():
    result = parse_rss_feed(VALID_XML)
    assert all(a.source == SourceEnum.HABR for a in result)


def test_empty_string_raises_xml_exception():
    with pytest.raises(XMLReaderException):
        parse_rss_feed("")


def test_invalid_xml_raises_xml_exception():
    with pytest.raises(XMLReaderException):
        parse_rss_feed("not xml at all <<<")
