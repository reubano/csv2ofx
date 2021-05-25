"""
Import transactions from Amazon Order History
as exported by Amazon Order History Reporter
(https://chrome.google.com/webstore/detail/amazon-order-history-repo/mgkilgclilajckgnedgjgnfdokkgnibi).

Honors a couple of environment variables:

 - ``AMAZON_EXCLUDE_CARDS``: comma-separated last-four digits
   of cards or payment methods to exclude in the output.
 - ``AMAZON_PURCHASES_ACCOUNT``: The OFX "account id" to use.
   Financial tools will use this account ID to associated with an
   account. If unspecified, defaults to "100000001".
"""

import os
import functools
from operator import itemgetter


@functools.lru_cache()
def cards():
    setting = os.environ.get('AMAZON_EXCLUDE_CARDS', None)
    return setting.split(',') if setting else []


def exclude_cards(row):
    return not any(card in row['payments'] for card in cards())


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
    'filter': exclude_cards,
}
