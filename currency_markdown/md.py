# Copyright 2019 Ben Caller
import gzip
import json

import requests
from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree

RE = r"^(?:.*?)££([0-9.]+)£([A-Z]{3})£([A-Z]+)££(?:.*)$"

SYMBOLS = {
    "AUD": "AU${amount}",
    "BRL": "R${amount}",
    "CAD": "CA${amount}",
    "CHF": "Fr. {amount}",
    "CNY": "CN¥{amount}",
    "CZK": "{amount} Kč",
    "EUR": "€{amount}",
    "GBP": "£{amount}",
    "HKD": "HK${amount}",
    "HUF": "{amount} Ft",
    "IDR": "Rp {amount}",
    "ILS": "₪{amount}",
    "INR": "₹{amount}",
    "JPY": "JP¥{amount}",
    "KRW": "₩{amount}",
    "MXN": "MX${amount}",
    "NZD": "NZ${amount}",
    "PEN": "S/{amount}",
    "PHP": "₱{amount}",
    "PLN": "{amount}zł",
    "RON": "{amount} lei",
    "SGD": "SG${amount}",
    "THB": "฿{amount}",
    "TRY": "₺{amount}",
    "TWD": "NT${amount}",
    "USD": "US${amount}",
}


def nice_money(amount, currency, fancy=False):
    if amount >= 1000 or (fancy and amount % 1 < 0.01):
        number_str = "{:,.0f}".format(amount)
    else:
        number_str = "{:,.2f}".format(amount)
    symbol_format = "{currency} {amount}"
    if fancy:
        symbol_format = SYMBOLS.get(currency, symbol_format)
    return symbol_format.format(currency=currency, amount=number_str)


def calculate(amount, currency_from, currency_to, rates):
    return amount / rates[currency_from] * rates[currency_to]


def rates_from_api():
    return requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()["rates"]


class CurrencyPattern(InlineProcessor):
    """..."""

    def __init__(self, md, rates, cache_file, **_):
        if rates is not None:
            self._rates = rates
        else:
            self._cached_get_rates(cache_file)
        super(InlineProcessor, self).__init__(RE, md)

    def _cached_get_rates(self, cache_file):
        if cache_file is not None:
            try:
                with gzip.open(cache_file, "rt") as gz_json_file:
                    self._rates = json.load(gz_json_file)
                    return
            except (FileNotFoundError, ValueError, OSError):
                self._rates = rates_from_api()
                with gzip.open(cache_file, "wt") as gz_json_file:
                    json.dump(self._rates, gz_json_file)
        else:
            raise ValueError("No currency rates or cache file")

    def handleMatch(self, m, data):
        """Handle currency matches."""

        amount = float(m.group(2))
        currency_from = m.group(3)
        to_currency_str = m.group(4)
        to_currencies = [to_currency_str[i:i+3] for i in range(0, len(to_currency_str), 3)]
        el = etree.Element("span")
        el.set("class", "currency")
        el.text = nice_money(amount, currency_from, fancy=True) + " "
        sub = etree.SubElement(el, "span")
        etree.SubElement(sub, "span").text = nice_money(amount, currency_from)
        for currency in to_currencies:
            etree.SubElement(sub, "br")
            amnt = calculate(amount, currency_from, currency, self._rates)
            etree.SubElement(sub, "span").text = nice_money(amnt, currency)
        return el, m.start(2) - 2, m.end(4) + 2


class CurrencyExtension(Extension):
    """..."""

    def __init__(self, *args, **kwargs):
        self.config = {
            "rates": [{}, "Map of currencies to USD rate"],
            "cache_file": ["", "File containing cached currency rates"],
        }
        super(CurrencyExtension, self).__init__(*args, **kwargs)
        if len(self.getConfig("rates")) == 0:
            self.setConfig("rates", None)
        if len(self.getConfig("cache_file")) == 0:
            self.setConfig("cache_file", None)

    def extendMarkdown(self, md):
        pattern = CurrencyPattern(md, **self.getConfigs())
        md.inlinePatterns.register(pattern, "currency", 90)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return CurrencyExtension(*args, **kwargs)
