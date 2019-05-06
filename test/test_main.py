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
    assert html.replace("\n", "") == surround(
        'a <span class="currency">Rp 60,000 '
        '<span><span>IDR 60,000</span><br /><span>USD 4.20</span></span></span> b'
    )


def test_multi_currency():
    ext = makeExtension(rates={
        "JPY": 123,
        "GBP": 1,
        "EUR": 0.1,
    })
    mkd = markdown.Markdown(extensions=[ext])
    html = mkd.convert("££61£GBP£EURJPY££")
    assert html.replace("\n", "") == surround(
        '<span class="currency">£61 <span><span>GBP 61.00</span><br />'
        '<span>EUR 6.10</span><br />'
        '<span>JPY 7,503</span></span></span>'
    )


def test_2():
    ext = makeExtension(rates={
        "ABC": 1,
        "DEF": 1,
    })
    mkd = markdown.Markdown(extensions=[ext])
    html = mkd.convert("££12345.0£ABC£DEFDEF££")
    assert html.replace("\n", "") == surround(
        '<span class="currency">ABC 12,345 <span><span>ABC 12,345</span><br />'
        '<span>DEF 12,345</span><br />'
        '<span>DEF 12,345</span></span></span>'
    )
