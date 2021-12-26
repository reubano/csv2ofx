from operator import itemgetter

mapping = {
    "is_split": True,
    "has_header": True,
    "account": itemgetter("AccountName"),
    "date": itemgetter("JournalDate"),
    "amount": itemgetter("NetAmount"),
    "payee": itemgetter("Description"),
    "notes": itemgetter("Product"),
    "class": itemgetter("Resource"),
    "id": itemgetter("JournalNumber"),
    "check_num": itemgetter("Reference"),
}
