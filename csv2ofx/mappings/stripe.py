# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.stripe
~~~~~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions obtained via Stripe card processing

Note that Stripe provides a Default set of columns or you can download
All columns. (as well as custom). The Default set does not include card
information, so provides no appropriate value for the PAYEE field for
an anonymous transaction (missing a customer).
It's suggested the All Columns format be used if not all transactions
identify a customer. This mapping sets PAYEE to Customer Name if it
exists, otherwise Card Name (if provided)
"""
from operator import itemgetter

mapping = {
    "has_header": True,
    "account": "Stripe",
    "id": itemgetter("id"),
    "date": itemgetter("created"),
    "amount": itemgetter("amount"),
    "currency": itemgetter("currency"),
    "payee": lambda tr: tr.get("customer_description")
    if len(tr.get("customer_description")) > 0
    else tr.get("card_name", ""),
    "desc": itemgetter("description"),
}
