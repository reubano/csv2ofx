# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.ingdirect
~~~~~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions obtained via ING Direct
(Australian bank)
"""
from operator import itemgetter

mapping = {
    "is_split": False,
    "has_header": True,
    "account": itemgetter("Account"),
    "date": itemgetter("Date"),
    "amount": lambda tr: tr["Credit"] + tr["Debit"],
    "desc": itemgetter("Description"),
}
