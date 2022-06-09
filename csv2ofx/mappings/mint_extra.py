# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.mintapi
~~~~~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions obtained via mint.com
"""
from operator import itemgetter
from csv2ofx.utils import convert_amount


mapping = {
    "is_split": False,
    "has_header": True,
    "split_account": itemgetter("Category"),
    "account": itemgetter("Account Name"),
    "date": itemgetter("Date"),
    "type": itemgetter("Transaction Type"),
    "amount": itemgetter("Amount"),
    "desc": itemgetter("Original Description"),
    "payee": itemgetter("Description"),
    "notes": itemgetter("Notes"),
    "first_row": 3,
    "last_row": -1,
    "filter": lambda trxn: convert_amount(trxn["Amount"]) < 2500,
}
