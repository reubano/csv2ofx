# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.stripe
~~~~~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions obtained via Stripe card processing

Note that Stripe provides a Default set of colums or you can download All columns. (as well as custom).
The Default set does not include card information, so provides no appropriate value for the MEMO field for an anonymous transaction (missing a customer).
It's suggested the All Columns format be used if not all transactions identify a customer.
This mapping sets MEMO to Customer Name if it exists, otherwise Card Name (if provided)
"""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from operator import itemgetter

mapping = {
    'has_header': True,
    'account': 'Stripe',
    'id': itemgetter('id'),
    'date': itemgetter('Created (UTC)'),
    'amount': itemgetter('Amount'),
    'currency': itemgetter('Currency'),
    'payee': lambda tr: tr.get('Customer Description') if len(tr.get('Customer Description')) > 0 else tr.get('Card Name', ""),
    'desc': itemgetter("Description")
}
