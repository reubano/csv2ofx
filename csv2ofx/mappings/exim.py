from __future__ import absolute_import, division, print_function, unicode_literals

from operator import itemgetter

mapping = {
    "bank": "Exim",
    "has_header": True,
    "currency": "USD",
    "account": itemgetter("Account"),
    "date": itemgetter("Date"),
    "amount": itemgetter("Amount"),
    "payee": itemgetter("Narration"),
    "notes": itemgetter("Notes"),
    "id": itemgetter("Reference Number"),
}
