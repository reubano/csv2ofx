"""
For PC Financial Mastercards
https://www.pcfinancial.ca/en/credit-cards
"""
from __future__ import absolute_import
from operator import itemgetter

mapping = {
    "has_header": True,
    "bank": "PC Financial",
    "currency": "CAD",
    "account": "Mastercard",
    "date": itemgetter("Date"),
    "amount": lambda r: float(r["Amount"]) * -1.0,
    "payee": itemgetter('"Merchant Name"'),
}
