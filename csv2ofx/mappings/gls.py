# coding: utf-8

from operator import itemgetter


def date_func(trxn):
    tag = trxn["Buchungstag"]
    return "{}/{}/{}".format(tag[3:5], tag[:2], tag[-4:])


mapping = {
    "has_header": True,
    "currency": "EUR",
    "delimiter": ";",
    "bank": "GLS Bank",
    "account": itemgetter("Kontonummer"),
    # Chop up the dotted German date format and put it in ridiculous M/D/Y order
    "date": date_func,
    # locale.atof does not actually know how to deal with German separators.
    # So we do it the crude way
    "amount": lambda r: r["Betrag"].replace(".", "").replace(",", "."),
    "desc": itemgetter("Buchungstext"),
    "notes": lambda r: " ".join(r["VWZ-{}".format(n)] for n in range(1, 15)),
    "payee": itemgetter("Auftraggeber/Empfänger"),
}
