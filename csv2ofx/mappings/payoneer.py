import os
from datetime import datetime
from operator import itemgetter


def is_credit(row):
    try:
        return (row.get("Debit Amount") or None) is None
    except ValueError:
        return True


def get_amount(row):
    if is_credit(row):
        return row.get("Credit Amount")

    return f'-{row.get("Debit Amount")}'


def payoneer_filter(transaction):
    try:
        float(transaction.get("Credit Amount") or transaction.get("Debit Amount"))
        return True
    except ValueError:
        return False


def get_date(row):
    date_str = f'{row.get("Transaction Date")} {row.get("Transaction Time")}'

    return datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S").strftime("%Y%m%d%H%M%S")


mapping = {
    "has_header": True,
    "filter": payoneer_filter,
    "is_split": False,
    "bank": "Payoneer Global Inc",
    "bank_id": "123",
    "currency": itemgetter("Currency"),
    "delimiter": ",",
    "account": os.environ.get("PAYONEER_ACCOUNT", "1000001"),
    "date": get_date,
    "parse_fmt": "%Y%m%d%H%M%S",
    "date_fmt": "%Y%m%d%H%M%S",
    "amount": get_amount,
    "desc": itemgetter("Description"),
    "payee": itemgetter("Target"),
    "balance": itemgetter("Running Balance"),
    "id": itemgetter("Transaction ID"),
    "type": lambda tr: "credit" if is_credit(tr) else "debit",
}
