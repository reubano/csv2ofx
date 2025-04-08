# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.mintapi
~~~~~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions on a german SumUp account
"""

from operator import itemgetter

from csv2ofx.utils import convert_amount

mapping = {
    "is_split": False,
    "has_header": True,
    "payee": lambda tr: " ".join(tr["Referenz"].split(" ")[:-1]),
    "date": lambda tr: tr["Datum der Transaktion"],
    "parse_fmt": "%d.%m.%y, %H:%M",
    "amount": lambda tr: float(tr["Zahlungsbetrag ausgehend"]) + float(tr["Zahlungsbetrag eingehend"]),
    "id": itemgetter("Transaktions-ID"),
    "currency": itemgetter("Zahlungswährung"),
    "desc": itemgetter("Zahlungsreferenz"),
    "type": lambda tr: "debit" if tr["Art der Transaktion"] == "Ausgehende Banküberweisung" else "credit",
    "balance": itemgetter("Verfügbares Guthaben"),
    "bank": "SumUp",
}
