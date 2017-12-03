# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.mintapi
~~~~~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions obtained via the mintapi python script
"""
from __future__ import absolute_import

from operator import itemgetter

mapping = {
    'is_split': False,
    'has_header': True,
    'account': itemgetter('account'),
    'category': itemgetter('category'),
    'split_account': itemgetter('category'),
    'type': lambda tr: 'debit' if tr['isDebit'] == 'TRUE' else 'credit',
    'date': itemgetter('odate'),
    'amount': itemgetter('amount'),
    'desc': itemgetter('omerchant'),
    'payee': itemgetter('merchant'),
    'notes': itemgetter('note'),
    'class': lambda tr: tr['labels'] if tr.get('labels', [])[1:-1] else '',
    'bank': itemgetter('fi'),
    'currency': 'USD',
    'id': itemgetter('id'),
    'shares': itemgetter('shares'),
    'symbol': itemgetter('symbol'),
}
