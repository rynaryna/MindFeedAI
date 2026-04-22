from parsers.hackernews_parser.extract_generic_text import extract_generic_text


def test_extracts_paragraph_text():
    html = "<html><body><p>Hello world</p><p>Second paragraph</p></body></html>"
    result = extract_generic_text(html)
    assert "Hello world" in result
    assert "Second paragraph" in result


def test_removes_script_tags():
    html = "<html><body><script>alert('xss')</script><p>Clean text</p></body></html>"
    result = extract_generic_text(html)
    assert "alert" not in result
    assert "Clean text" in result


def test_removes_style_tags():
    html = "<html><head><style>body { color: red; }</style></head><body><p>Content</p></body></html>"
    result = extract_generic_text(html)
    assert "color" not in result


def test_removes_nav_footer_header():
    html = """<html><body>
      <header>Site header</header>
      <nav>Navigation links</nav>
      <p>Main content</p>
      <footer>Footer text</footer>
    </body></html>"""
    result = extract_generic_text(html)
    assert "Site header" not in result
    assert "Navigation links" not in result
    assert "Footer text" not in result
    assert "Main content" in result


def test_empty_input_returns_empty_string():
    assert extract_generic_text("") == ""


def test_collapses_multiple_newlines():
    html = "<html><body><p>One</p><p>Two</p><p>Three</p></body></html>"
    result = extract_generic_text(html)
    assert "\n\n" not in result
