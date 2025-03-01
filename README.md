# csv2ofx

[![GHA](https://github.com/reubano/csv2ofx/actions/workflows/main.yml/badge.svg)](https://github.com/reubano/csv2ofx/actions?query=workflow%3A%22tests%22)
[![versions](https://img.shields.io/pypi/pyversions/csv2ofx.svg)](https://pypi.python.org/pypi/csv2ofx)
[![pypi](https://img.shields.io/pypi/v/csv2ofx.svg)](https://pypi.python.org/pypi/csv2ofx)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## INTRODUCTION

[csv2ofx](http://github.com/reubano/csv2ofx) is a [Python library](#library-examples) and [command line interface program](#cli-examples) that converts CSV files to OFX and QIF files for importing into GnuCash or Moneydance or similar financial accounting programs. csv2ofx has built in support for importing csv files from mint, yoodlee, and xero.

## Requirements

csv2ofx is pure Python and is [tested](https://github.com/reubano/csv2ofx/actions?query=workflow%3A%22tests%22) on a number of Pythons and platforms.

## INSTALLATION

  pip install csv2ofx

(recommended in a [virtualenv](https://virtualenv.pypa.io/en/latest/))

## Usage

csv2ofx is intended to be used either directly from Python or from the command line.

### Library Examples

*normal OFX usage*

```python
import itertools as it

from meza.io import read_csv, IterStringIO
from csv2ofx import utils
from csv2ofx.ofx import OFX
from csv2ofx.mappings.default import mapping

ofx = OFX(mapping)
records = read_csv('path/to/file.csv', has_header=True)
groups = ofx.gen_groups(records)
trxns = ofx.gen_trxns(groups)
cleaned_trxns = ofx.clean_trxns(trxns)
data = utils.gen_data(cleaned_trxns)
content = it.chain([ofx.header(), ofx.gen_body(data), ofx.footer()])

for line in IterStringIO(content):
    print(line)
```

*normal QIF usage*

```python
import itertools as it

from tabutils.io import read_csv, IterStringIO
from csv2ofx import utils
from csv2ofx.qif import QIF
from csv2ofx.mappings.default import mapping

qif = QIF(mapping)
records = read_csv('path/to/file.csv', has_header=True)
groups = qif.gen_groups(records)
trxns = qif.gen_trxns(groups)
cleaned_trxns = qif.clean_trxns(trxns)
data = utils.gen_data(cleaned_trxns)
content = it.chain([qif.gen_body(data), qif.footer()])

for line in IterStringIO(content):
    print(line)
```

### CLI Examples

*show help*

  csv2ofx -h

```bash
usage: csv2ofx [options] <source> <dest>

description: csv2ofx converts a csv file to ofx and qif

positional arguments:
  source                the source csv file (default: stdin)
  dest                  the output file (default: stdout)

options:
  -h, --help            show this help message and exit
  -a, --account TYPE    default account type 'CHECKING' for OFX and 'Bank' for QIF.
  -e, --end DATE        end date (default: today)
  -B, --ending-balance BALANCE
                        ending balance (default: None)
  -l, --language LANGUAGE
                        the language (default: ENG)
  -s, --start DATE      the start date
  -y, --dayfirst        interpret the first value in ambiguous dates (e.g. 01/05/09) as the day
  -m, --mapping MAPPING_NAME
                        the account mapping (default: default)
  -x, --custom FILE_PATH
                        path to a custom mapping file
  -c, --collapse FIELD_NAME
                        field used to combine transactions within a split for double entry statements
  -C, --chunksize ROWS  number of rows to process at a time (default: 2 ** 14)
  -r, --first-row ROWS  the first row to process (zero based)
  -R, --last-row ROWS   the last row to process (zero based, negative values count from the end)
  -O, --first-col COLS  the first column to process (zero based)
  -L, --list-mappings   list the available mappings
  -V, --version         show version and exit
  -q, --qif             enables 'QIF' output instead of 'OFX'
  -M, --ms-money        enables MS Money compatible 'OFX' output
  -o, --overwrite       overwrite destination file if it exists
  -D, --server-date DATE
                        OFX server date (default: source file mtime)
  -E, --encoding ENCODING
                        File encoding (default: utf-8)
  -d, --debug           display the options and arguments passed to the parser
  -v, --verbose         verbose output
```

*normal usage*

	csv2ofx file.csv file.ofx

*print output to stdout*

	csv2ofx ~/Downloads/transactions.csv

*read input from stdin*

	cat file.csv | csv2ofx

*qif output*

	csv2ofx -q file.csv

*specify date range from one year ago to yesterday with qif output*

	csv2ofx -s '-1 year' -e yesterday -q file.csv

*use yoodlee settings*

	csv2ofx -m yoodlee file.csv


#### Special cases

Some banks, like *UBS Switzerland*, may provide CSV exports that are not
readily tractable by csv2ofx because of extra header or trailing lines,
redundant or unwanted columns. These input files can be preprocessed with the
shipped `utilz/csvtrim` shell script. F.i., with mapping `ubs-ch-fr`:

    csvtrim untrimmed.csv | csv2ofx -m ubs-ch-fr


## CUSTOMIZATION

### Code modification

To import csv files with field names different from the default, either modify the mapping file or create your own. New mappings must be placed in the `csv2ofx/mappings` folder. The mapping object consists of a dictionary whose keys are OFX/QIF attributes and whose values are functions that should return the corresponding value from a record (csv row). The mapping function will take in a record, e.g.,

```python
{'Account': 'savings 2', 'Date': '1/3/15', 'Amount': 5000}
```

The most basic mapping function just returns a specific field or value, e.g.,

```python
from operator import itemgetter

mapping = {
    'bank': 'BetterBank',
    'account': itemgetter('Account'),
    'date': itemgetter('Date'),
    'amount': itemgetter('Amount')}
```

But more complex parsing is also possible, e.g.,

```python
mapping = {
    'account': lambda r: r['Details'].split(':')[0],
    'date': lambda r: '%s/%s/%s' % (r['Month'], r['Day'], r['Year']),
    'amount': lambda r: r['Amount'] * 2,
    'first_row': 1,
    'last_row': 10,
    'filter': lambda r: float(r['Amount']) > 10,
}
```

### Required field attributes

attribute | description | default field | example
----------|-------------|---------------------|--------
`account`|transaction account|Account|BetterBank Checking
`date`|transaction date|Date|itemgetter('Transaction Date')
`amount`|transaction amount|Amount|itemgetter('Transaction Amount')

### Optional field attributes

attribute | description | default field | default value | example
----------|-------------|---------------|---------------|--------
`desc`|transaction description|Reference|n/a|shell station
`payee`|transaction payee|Description|n/a|Shell
`notes`|transaction notes|Notes|n/a|for gas
`check_num`|the check or transaction number|Row|n/a|2
`id`|transaction id|`check_num`|Num|n/a|531
`bank`|the bank name|n/a|`account`|Bank
`account`|transaction account type|n/a|checking|savings
`account_id`|transaction account id|n/a|hash of `account`|bb_checking
`type`|transaction type (either debit or credit)|n/a|CREDIT if amount > 0 else DEBIT|debit
`balance`|account balance|n/a|n/a|$23.00
`class`|transaction class|n/a|n/a|travel

### Optional value attributes

attribute | description | default value | example
----------|-------------|---------------|--------
`has_header`|does the csv file have a header row|True
`custom_header`|header row to use (e.g. if not provided in csv)|None|["Account","Date","Amount"]
`is_split`|does the csv file contain split (double entry) transactions|False
`currency`|the currency ISO code|USD|GBP
`delimiter`|the csv field delimiter|,|;
`date_fmt`|custom QIF date output format|%m/%d/%y|%m/%d/%Y
`dayfirst`|interpret the first value in ambiguous dates (e.g. 01/05/09) as the day (ignored if `parse_fmt` is present)|False|True
`parse_fmt`|transaction date parsing format||%m/%d/%Y
`first_row`|the first row to process (zero based)|0|2
`last_row`|the last row to process (zero based, negative values count from the end)|inf|-2
`first_col`|the first column to process (zero based)|0|2
`filter`|keep transactions for which function returns true||lambda tr: float(tr['amount']) > 10

## Scripts

### Running tests

  tox

## Contributing

Please mimic the coding style/conventions used in this repo. When adding new classes or functions, please add the appropriate doc blocks with examples.

Ready to contribute? Here's how:

1. Fork and clone.

```bash
git clone https://github.com/reubano/csv2ofx
cd csv2ofx
```

2. Run tox.

Either install [tox](https://tox.wiki) or install [pipx](https://pipx.pypa.io) and use it to `pipx run tox`:

```bash
tox
```

Tox will run the tests and other checks (linter) in different Python environments. It will create Python environments in `.tox/*` (e.g. `.tox/py313`) and install csv2ofx there. To run in just the main python environment:

```bash
tox -e py
```

Feel free to activate one of those environments or create a separate one.

3. Create a branch for local development

```bash
git checkout -b name-of-your-bugfix-or-feature
```

4. Make your changes, run tests (see above), and submit a pull request through the GitHub website.

### Adding Mappings

How to contribute a mapping:

1. Add the mapping in `csv2ofx/mappings/`
2. Add a simple example CSV file in `data/test/`.
3. Add the OFX or QIF file that results from the mapping and example CSV file in `data/converted/`.
4. Add a `csv2ofx` call for your mapping to the tests in `tests/test.py`, in `PRE_TESTS`. When adding an OFX (not QIF) converted file, pay attention to the `-e` (end date) and `-D` (server date) arguments in the test- otherwise tests may pass locally but fail on the build server.
5. Ensure your test succeeds (see above).

## License

csv2ofx is distributed under the [MIT License](http://opensource.org/licenses/MIT), the same as [meza](https://github.com/reubano/meza).
