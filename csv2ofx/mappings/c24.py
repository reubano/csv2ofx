"""Mapping for the German C24 bank.

The C24 bank supports sub-accounts. Every transaction in the CSV file has a
user-configurable account name "Kontoname". Transactions from all sub-accounts
are stored chronologically in this list. The transaction list includes both
intrabank transfers between these accounts ("internal") as well as all other
transactions ("external").

OFX files have a special way of identifying intrabank transfers `<INTRATRNRS>`
but the file can either only include intrabank transfers or normal ones. The
expected behaviour would be to list all transactions, with intrabank and normal
transactions having the same formatting. In some cases however, the user may
want to have a properly formatted list of intrabank transfers as well. Toward
this, the environment variable `TRANSACTIONS` can be used.

Possible `TRANSACTIONS` env var values:
- "all" (default): Include all transactions as normal statements. There is no
    way to differentiate intrabank transfers.
- "internal": Only include intrabank transfers.
- "external": Only include normal transfers. Accounts will have weird balances.
"""

from __future__ import annotations

from operator import itemgetter
from os import environ
from sys import stderr

_INCLUDE_INTERNAL_TX = True
_INCLUDE_EXTERNAL_TX = True
tmp = environ.get("TRANSACTIONS", "all").lower()
if tmp == "internal":
    _INCLUDE_INTERNAL_TX = True
    _INCLUDE_EXTERNAL_TX = False
elif tmp == "external":
    _INCLUDE_INTERNAL_TX = False
    _INCLUDE_EXTERNAL_TX = True
elif tmp != "all":
    print("TRANSACTIONS: invalid environment variable value!", file=stderr)


# "Pocket-Umbuchung" is a manual transfer between sub accounts, "Sparen" is when
# the user configured automatic transfer rules at certain events.
def _is_split_tx(tx: dict[str, str]) -> bool:
    tx_type = tx["Transaktionstyp"]
    return tx_type in {"Pocket-Umbuchung", "Sparen"}


def _get_split_recipient(tx: dict[str, str]) -> str | None:
    if not _is_split_tx(tx):
        return None
    split_recipient = tx["Zahlungsempfänger"]
    return split_recipient


def _filter_tx(tx: dict[str, str]) -> bool:
    is_split = _is_split_tx(tx)
    if is_split:
        return _INCLUDE_INTERNAL_TX
    else:
        return _INCLUDE_EXTERNAL_TX


# We MUST NOT use the "Kontonummer" as account ID, because for transfers between
# sub accounts there is no recipient "Kontonummer". By using the default
# generated hash of the sender name "Kontoname" and the recipient name
# "Zahlungsempfänger", internal transfers can be associated correctly.
mapping = {
    "has_header": True,
    "currency": "EUR",
    "delimiter": ",",
    "bank": "C24",
    "account": itemgetter("Kontoname"),
    "date": itemgetter("Buchungsdatum"),
    "parse_fmt": "%d.%m.%Y",
    "amount": lambda tx: tx["Betrag"].replace(".", "").replace(",", "."),
    "desc": itemgetter("Verwendungszweck"),
    "payee": itemgetter("Zahlungsempfänger"),
    "filter": _filter_tx,
    # Setting this entry to anything other than `None` implicitly toggles the
    # intrabank transfer output, which cannot include normal/external
    # statements. Sets this getter only when not including these normal
    # statements.
    "split_account": _get_split_recipient if not _INCLUDE_EXTERNAL_TX else None,
    # I don't like how the values below just get added to the memo. Feel free
    # to re-include them.
    #
    # An automatic/manual categorization of the transaction.
    # "class": itemgetter("Unterkategorie"),
    #
    # This seems to be a more human-readable name of the payee. In credit card
    # statements, this may be the name of the credit card owner while the payee
    # ("Zahlungsempfänger") is the name of the credit card provider.
    # "notes": itemgetter("Beschreibung"),
}
