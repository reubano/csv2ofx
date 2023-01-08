# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.ingdirect
~~~~~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions obtained via ING Direct
(Spanish bank)
"""
from operator import itemgetter
import json
import hashlib


def find_type(transaction):
    amount = float(transaction.get("amount"))
    return "credit" if amount > 0 else "debit"


def gen_transaction_id(transaction):
    hasher = hashlib.sha256()
    stringified = json.dumps(transaction).encode("utf-8")
    hasher.update(stringified)
    return hasher.hexdigest()


def get_payee(transaction):
    cadena = transaction.get('desc')
    subcadenas = ['Abono por campaña', 'Devolución Tarjeta', 
               'Nomina recibida', 'Traspaso recibido', 'Pago en', 
               'Recibo', 'Reintegro efectivo', 'Transferencia Bizum emitida', 
               'Transferencia emitida a', 'Transferencia recibida de']
    for subcadena in subcadenas:
        if subcadena in cadena:
            payee = cadena.replace(subcadena, '')
            break
        else:
            payee = cadena
    return payee


def get_transaction_type(transaction):
    cadena = transaction.get('desc')
    subcadenas = ['Abono por campaña', 'Devolución Tarjeta', 
               'Nomina recibida', 'Traspaso recibido', 'Pago en', 
               'Recibo', 'Reintegro efectivo', 'Transferencia Bizum emitida', 
               'Transferencia emitida a', 'Transferencia recibida de']
    for subcadena in subcadenas:
        if subcadena in cadena:
            notes = subcadena
    return notes


mapping = {
    "has_header": True,
    "is_split": False,
    "bank": "ING",
    "currency": "EUR",
    "delimiter": ",",
    "account": "ING checking",
    "type": find_type,
    "date": itemgetter("date"),
    "amount": itemgetter("amount"),
    "payee": get_payee,
    # 'desc': get_transaction_type,
    "class": itemgetter("class"),
    "id": gen_transaction_id,
}

