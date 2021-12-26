# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.mint_headerless
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions obtained via mint.com
"""
from operator import itemgetter

mapping = {
    "is_split": False,
    "has_header": False,
    "split_account": itemgetter("column_6"),
    "account": itemgetter("column_7"),
    "date": itemgetter("column_1"),
    "type": itemgetter("column_5"),
    "amount": itemgetter("column_4"),
    "desc": itemgetter("column_3"),
    "payee": itemgetter("column_2"),
}
