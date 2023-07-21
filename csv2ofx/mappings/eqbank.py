from operator import itemgetter

mapping = {
    "has_header": True,
    "bank": "EQ Bank",
    "currency": "CAD",
    "delimiter": ",",
    "account": lambda tr: "EQ",
    "date": itemgetter("Date"),
    "desc": itemgetter("Description"),
    "type": lambda tr: "DEBIT" if tr.get("Transfer").startswith("-") else "CREDIT",
    "amount": lambda tr: tr.get("Transfer"),
    "balance": itemgetter("Balance"),
}
