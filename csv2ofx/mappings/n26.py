from operator import itemgetter
import json
import hashlib


def find_type(transaction):
    amount = float(transaction.get("Amount (EUR)"))
    return "credit" if amount > 0 else "debit"


def gen_transaction_id(transaction):
    hasher = hashlib.sha256()
    stringified = json.dumps(transaction).encode("utf-8")
    hasher.update(stringified)
    return hasher.hexdigest()


mapping = {
    "has_header": True,
    "is_split": False,
    "bank": "N26",
    "currency": "EUR",
    "delimiter": ",",
    "account": "N26 checking",
    "type": find_type,
    "date": itemgetter("Date"),
    "amount": itemgetter("Amount (EUR)"),
    "payee": itemgetter("Payee"),
    "notes": itemgetter("Payment reference"),
    # 'desc': itemgetter('Payment reference'),
    "class": itemgetter("Category"),
    "id": gen_transaction_id,
    # 'check_num': itemgetter('Field'),
}
