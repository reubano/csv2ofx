from operator import itemgetter


mapping = {
    "has_header": True,
    "is_split": False,
    "delimiter": ";",
    "bank": "Boursorama",
    "account": itemgetter("accountNum"),
    "account_id": itemgetter("accountNum"),
    "date": itemgetter("dateOp"),
    "type": "checking",
    "amount": lambda r: r["amount"].replace(" ", "").replace(",", "."),
    "currency": "EUR",
    "desc": itemgetter("label"),
    "date_fmt": "%Y%Y-%m%m-%d%d",
    "balance": itemgetter("accountbalance"),
}
