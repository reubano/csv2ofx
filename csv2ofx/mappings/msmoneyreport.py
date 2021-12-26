from operator import itemgetter

mapping = {
    "has_header": True,
    "bank": lambda tr: tr["Account"].split(" - ")[0],
    "account": lambda tr: tr["Account"].split(" - ")[1:],
    "currency": itemgetter("Currency"),
    "class": itemgetter("Projects"),
    "check_num": itemgetter("Num"),
    "type": lambda tr: "debit" if tr.get("Debit") else "credit",
    "amount": itemgetter("Amount"),
    "notes": itemgetter("Memo"),
    "date": itemgetter("Date"),
    "desc": itemgetter("Category"),
    "payee": itemgetter("Payee"),
}
