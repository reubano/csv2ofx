# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.mdb
~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions obtained via moneydashboard.com
"""
from operator import itemgetter

mapping = {
    "is_split": False,
    "has_header": True,
    "currency": "GBP",
    "account": itemgetter("Account"),
    "date": itemgetter("Date"),
    "amount": itemgetter("Amount"),
    "desc": itemgetter("OriginalDescription"),
    "payee": itemgetter("CurrentDescription"),
    "class": itemgetter("Tag"),
}
