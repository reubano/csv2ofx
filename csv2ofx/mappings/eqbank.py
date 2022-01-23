from operator import itemgetter

mapping = {
    "has_header": True,
    "bank": "EQ Bank",
    "currency": "CAD",
    "delimiter": ",",
    "account": lambda tr: "EQ",
    "date": itemgetter("Date"),
    "desc": itemgetter("Description"),
    "type": lambda tr: "DEBIT" if tr.get("Out") else "CREDIT",
    "amount": lambda tr: tr.get("In") or tr.get("Out"),
    "balance": itemgetter("Balance"),
}
