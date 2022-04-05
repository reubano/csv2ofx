from operator import itemgetter

mapping = {
    "has_header": True,
    "is_split": False,
    "bank": "Santander",
    "currency": "BRL",
    "delimiter": ";",
    "account": "Santander Bank",
    "date": itemgetter("Date"),
    "date_fmt": "%d/%m/%y",
    "type": lambda tr: "DEBIT" if tr.get("Debit") else "CREDIT",
    "amount": lambda tr: tr.get("Debit") or tr.get("Credit"),
    "desc": itemgetter("Name"),
    "notes": itemgetter("Memo")
}
