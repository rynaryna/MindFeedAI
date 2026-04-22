import pytest
from parsers.habr_parser.extract_article_text import extract_article_text
from exceptions.parser_exceptions import HTMLReaderException


ARTICLE_HTML = """<html><body>
  <div class="article-formatted-body">
    <p>Hello world</p>
    <figure><img src="foo.png"/></figure>
    <p>Second paragraph</p>
  </div>
</body></html>"""


def test_extracts_text_from_article_div():
    result = extract_article_text(ARTICLE_HTML)
    assert "Hello world" in result
    assert "Second paragraph" in result


def test_removes_figure_elements():
    result = extract_article_text(ARTICLE_HTML)
    assert "foo.png" not in result


def test_empty_input_raises_html_exception():
    with pytest.raises(HTMLReaderException):
        extract_article_text("")


def test_missing_article_div_returns_empty_string():
    html = "<html><body><p>No article div here</p></body></html>"
    result = extract_article_text(html)
    assert result == ""


def test_collapses_multiple_newlines():
    html = """<html><body><div class="article-formatted-body">
      <p>First paragraph</p>
      <p>Second paragraph</p>
    </div></body></html>"""
    result = extract_article_text(html)
    assert "\n\n" not in result
