"""
Import transactions from Amazon Order History
as exported by Amazon Order History Reporter
(https://chrome.google.com/webstore/detail/amazon-order-history-repo/mgkilgclilajckgnedgjgnfdokkgnibi).

Honors some environment variables:

 - ``AMAZON_INCLUDE_CARDS``: comma-separated last-four digits
   of cards or payment methods to include in the output. If not
   supplied, defaults to all cards.
 - ``AMAZON_EXCLUDE_CARDS``: comma-separated last-four digits
   of cards or payment methods to exclude in the output (supersedes
   include).
 - ``AMAZON_PURCHASES_ACCOUNT``: The OFX "account id" to use.
   Financial tools will use this account ID to associated with an
   account. If unspecified, defaults to "100000001".
"""

import os
import functools
from operator import itemgetter


All = ['']
"""
A special value matching all cards.
"""


@functools.lru_cache()
def exclude_cards():
    setting = os.environ.get('AMAZON_EXCLUDE_CARDS', None)
    return setting.split(',') if setting else []


@functools.lru_cache()
def include_cards():
    setting = os.environ.get('AMAZON_INCLUDE_CARDS', None)
    return setting.split(',') if setting else All


def filter_payment(row):
    include = any(card in row['payments'] for card in include_cards())
    exclude = any(card in row['payments'] for card in exclude_cards())
    return include and not exclude


mapping = {
    'has_header': True,
    'delimiter': ',',
    'bank': 'Amazon Purchases',
    'account_id': os.environ.get('AMAZON_PURCHASES_ACCOUNT', '100000001'),
    'date': itemgetter('date'),
    'amount': itemgetter('total'),
    'payee': 'Amazon',
    'desc': itemgetter('items'),
    'id': itemgetter('order id'),
    'type': 'DEBIT',
    'last_row': -1,
    'filter': filter_payment,
}
