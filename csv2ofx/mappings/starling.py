from operator import itemgetter


def fixdate(ds):
    dmy = ds.split("/")
    # BUG (!?): don't understand but stolen from ubs-ch-fr.py
    return ".".join((dmy[1], dmy[0], dmy[2]))


mapping = {
    "has_header": True,
    "date": lambda tr: fixdate(tr["Date"]),
    "amount": itemgetter("Amount (GBP)"),
    "desc": itemgetter("Reference"),
    "payee": itemgetter("Counter Party"),
}
