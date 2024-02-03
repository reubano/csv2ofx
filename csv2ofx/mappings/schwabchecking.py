from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from operator import itemgetter
import re

# Default value if account_id not found in header rows.
schwab_account_id = "12345"


def is_real(transaction):
    # Filter-out header line & lines that only have one column
    type = transaction.get('Type')
    return type and (type != "Type")


def schwab_filter(transaction):
    if is_real(transaction):
        return True

    # Sanity check header row in CSV matches custom_header
    line = transaction.get(mapping["custom_header"][0])
    if line in mapping["custom_header"]:
        for column in mapping["custom_header"]:
            found_col = transaction.get(column)
            if found_col != column:
                raise ValueError("Header row mismatch (expected: '" + column +
                        "', found: '" + found_col + "')")

    # Look for account_id in one of the lines being filtered out
    global schwab_account_id
    match = re.search(r'^Transactions  for .* account (\.*\d*) as of', line)
    if match:
        schwab_account_id = match.group(1)
    return False


def get_account_id(transaction):
    global schwab_account_id
    return schwab_account_id


mapping = {
    # Technically Schwab Bank CSVs do have a header, but we want to extract
    # the account_id from the line that comes before the header, so we use
    # custom_header instead of parsing it from the second line of the CSV.
    'custom_header': ["Date","Type","Check #","Description","Withdrawal (-)",
        "Deposit (+)","RunningBalance"],
    'has_header': False,
    'filter': schwab_filter,
    'is_split': False,
    'bank': 'Charles Schwab Bank, N.A.',
    'bank_id': '121202211',
    'account_id': get_account_id,
    'currency': 'USD',
    'account': 'Charles Schwab Checking',
    # Schwab Bank includes three lines of text in their CSV which otherwise
    # break date parsing.  Filtering by lines with no "Type" (and faking out
    # the date for those lines) avoids the problem.
    'date': lambda tr: tr.get('Date') if is_real(tr) else "1-1-1970",
    'check_num': itemgetter('Check #'),
    'payee': itemgetter('Description'),
    'desc': itemgetter('Description'),
    'type': lambda tr: 'debit' if tr.get('Withdrawal (-)') != '' else 'credit',
    'amount': lambda tr: tr.get('Deposit (+)') or tr.get('Withdrawal (-)'),
    'balance': itemgetter('RunningBalance'),
}
