from bs4 import BeautifulSoup

from pokecrawler.sanitizer.html_cleaner import clean


class TestClean:
    def test_removes_display_none(self):
        soup = BeautifulSoup(
            '<div><span style="display:none">hidden</span><p>visible</p></div>',
            "html.parser",
        )
        clean(soup)
        assert soup.find("span") is None
        assert soup.find("p") is not None

    def test_removes_display_none_with_spaces(self):
        soup = BeautifulSoup(
            '<div><span style="display: none">hidden</span></div>',
            "html.parser",
        )
        clean(soup)
        assert soup.find("span") is None

    def test_removes_display_none_uppercase(self):
        soup = BeautifulSoup(
            '<div><span style="DISPLAY:NONE">hidden</span></div>',
            "html.parser",
        )
        clean(soup)
        assert soup.find("span") is None

    def test_keeps_visible_elements(self):
        soup = BeautifulSoup(
            '<div><p style="color:red">visible</p></div>',
            "html.parser",
        )
        clean(soup)
        assert soup.find("p") is not None

    def test_no_style_attribute_untouched(self):
        soup = BeautifulSoup("<div><p>visible</p></div>", "html.parser")
        clean(soup)
        assert soup.find("p") is not None

    def test_returns_soup(self):
        soup = BeautifulSoup("<div></div>", "html.parser")
        result = clean(soup)
        assert result is soup
