from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from operator import itemgetter

mapping = {
    'has_header': True,
    'is_split': False,
    'bank': 'CapitalOne',
    'currency': 'USD',
    'delimiter': ',',
    'account': itemgetter('Card No.'),
    'date': itemgetter('Posted Date'),
    'type': lambda tr: 'DEBIT' if tr.get('Debit') else 'CREDIT',
    'amount': lambda tr: tr.get('Debit') or tr.get('Credit'),
    'desc': itemgetter('Description'),
    'payee': itemgetter('Description'),
}
