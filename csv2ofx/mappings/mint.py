from __future__ import absolute_import

from operator import itemgetter

mapping = {
    'is_split': False,
    'has_header': True,
    'account': itemgetter('Account Name'),
    'date': itemgetter('Date'),
    'type': itemgetter('Transaction Type'),
    'amount': itemgetter('Amount'),
    'desc': itemgetter('Original Description'),
    'payee': itemgetter('Description'),
    'notes': itemgetter('Notes'),
}
