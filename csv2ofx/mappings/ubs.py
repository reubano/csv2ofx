from operator import itemgetter

mapping = {
    "bank": "UBS",
    "has_header": True,
    "currency": "Ccy.",
    "delimiter": ";",
    "type": lambda tr: "debit" if tr.get("Debit") else "credit",
    "amount": lambda tr: tr.get("Debit", tr["Credit"]),
    "notes": lambda tr: " / ".join(
        filter(None, [tr["Description 1"], tr["Description 2"], tr["Description 3"]])
    ),
    "date": itemgetter("Value date"),
    "desc": itemgetter("Description"),
    "payee": lambda tr: tr.get("Recipient", tr["Entered by"]),
}
