from operator import itemgetter

mapping = {
    "has_header": False,
    "delimiter": "\t",
    "bank": "ABN Amro",
    "currency": itemgetter("field_1"),
    "account": itemgetter("field_0"),
    "date": itemgetter("field_2"),
    "amount": itemgetter("field_6"),
    "payee": itemgetter("field_7"),
}
