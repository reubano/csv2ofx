from operator import itemgetter


def note_func(tr):
    notes = [tr.get("desc1"), tr.get("desc1"), tr.get("desc1")]
    return " / ".join(filter(None, notes))


mapping = {
    "has_header": True,
    "is_split": True,
    "bank": lambda tr: tr["Account Name"].split(" - ")[0],
    "notes": note_func,
    "account": lambda tr: tr["Account Name"].split(" - ")[1:],
    "date": itemgetter("Date"),
    "type": itemgetter("Transaction Type"),
    "amount": itemgetter("Amount"),
    "currency": itemgetter("Currency"),
    "desc": itemgetter("Original Description"),
    "payee": itemgetter("User Description"),
    "class": itemgetter("Classification"),
    "id": itemgetter("Transaction Id"),
}
