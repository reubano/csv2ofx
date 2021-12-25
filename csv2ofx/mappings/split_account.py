from __future__ import absolute_import, division, print_function, unicode_literals

from operator import itemgetter

mapping = {
    "has_header": True,
    "is_split": False,
    "bank": "Bank",
    "currency": "USD",
    "delimiter": ",",
    "split_account": itemgetter("Category"),
    "account": itemgetter("Account"),
    "date": itemgetter("Date"),
    "amount": itemgetter("Amount"),
    "desc": itemgetter("Reference"),
    "payee": itemgetter("Description"),
    "notes": itemgetter("Notes"),
    "check_num": itemgetter("Num"),
    "id": itemgetter("Row"),
}
