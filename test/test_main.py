# Copyright (c) 2019 Ben Caller
import markdown
import pytest

from currency_markdown.md import makeExtension


def surround(s):
    return '<p>{}</p>'.format(s)


@pytest.fixture
def md():
    ext = makeExtension(cache_file="test/currencies.json.gz")
    return markdown.Markdown(extensions=[ext])


def test_currency(md):
    html = md.convert("a ££60000£IDR£USD££ b")
    assert html == surround(
        'a <span class="currency">IDR 60,000 <span><span>USD 4.20</span></span></span> b'
    )


def test_multi_currency():
    ext = makeExtension(rates={
        "IDR": 123,
        "GBP": 456,
        "EUR": 0.1,
    })
    mkd = markdown.Markdown(extensions=[ext])
    html = mkd.convert("££60000£IDR£GBPEUR££")
    print(html)
    assert html == surround(
        '<span class="currency">IDR 60,000 <span><span>GBP 222,439</span><br />\n'
        '<span>EUR 48.78</span></span></span>'
    )
