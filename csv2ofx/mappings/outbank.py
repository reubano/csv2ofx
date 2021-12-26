# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.ingdirect
~~~~~~~~~~~~~~~~~~~~~~~~
Provides a mapping for transactions obtained from Outbank, a
banking application that is able to export to CSV.
Mapping build for version 2.19.
"""
from operator import itemgetter

mapping = {
    "is_split": False,
    "has_header": True,
    "delimiter": ";",
    "account": itemgetter("Account"),
    "currency": itemgetter("Currency"),
    "payee": itemgetter("Name"),
    "date": itemgetter("Date"),
    "amount": itemgetter("Amount"),
    "desc": itemgetter("Reason"),
}
