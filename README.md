# csv2ofx

## INTRODUCTION

[csv2ofx](http://github.com/reubano/csv2ofx) is a [Python library](#library-examples) and [command line interface program](#cli-examples) that converts CSV files to OFX and QIF files for importing into GnuCash or similar financial accounting programs. csv2ofx has built in support for importing csv files from mint, yoodlee, and xero. csv2ofx has been tested on the following configuration:

* MacOS X 10.9.5
* Python 2.7.10

## Requirements

csv2ofx requires the following programs in order to run properly:

* [Python >= 2.7](http://www.python.org/download) (MacOS X comes with python preinstalled)

## INSTALLATION

(You are using a [virtualenv](http://www.virtualenv.org/en/latest/index.html), right?)

    sudo pip install csv2ofx

## Usage

csv2ofx is intended to be used either directly from Python or from the command line.

### Library Examples

*normal OFX usage*

```python
from __future__ import absolute_import, print_function

import itertools as it

from meza.io import read_csv, IterStringIO
from csv2ofx import utils
from csv2ofx.ofx import OFX
from csv2ofx.mappings.default import mapping

ofx = OFX(mapping)
records = read_csv('path/to/file.csv')
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
from __future__ import absolute_import, print_function

import itertools as it

from tabutils.io import read_csv, IterStringIO
from csv2ofx import utils
from csv2ofx.qif import QIF
from csv2ofx.mappings.default import mapping

qif = QIF(mapping)
records = read_csv('path/to/file.csv')
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
  source                the source csv file (defaults to stdin)
  dest                  the output file (defaults to stdout)

optional arguments:
  -h, --help            show this help message and exit
  -a TYPE, --account TYPE
                        default account type 'CHECKING' for OFX and 'Bank' for QIF.
  -e DATE, --end DATE   end date
  -l LANGUAGE, --language LANGUAGE
                        the language
  -s DATE, --start DATE
                        the start date
  -m MAPPING, --mapping MAPPING
                        the account mapping
  -c FIELD_NAME, --collapse FIELD_NAME
                        field used to combine transactions within a split for double entry statements
  -S FIELD_NAME, --split FIELD_NAME
                        field used for the split account for single entry statements
  -C ROWS, --chunksize ROWS
                        number of rows to process at a time
  -V, --version         show version and exit
  -q, --qif             enables 'QIF' output instead of 'OFX'
  -o, --overwrite       overwrite destination file if it exists
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

## CUSTOMIZATION

### Code modification

If you would like to import csv files with field names different from the default, you can modify the mapping file or create your own. New mappings must be placed in the `csv2ofx/mappings` folder. The mapping object consists of a dictionary whose keys are OFX/QIF attributes and whose values are functions which should return the corresponding value from a record (csv row). The mapping function will take in a record, e.g.,

```python
{'Account': 'savings 2', 'Date': '1/3/15', 'Amount': '5,000'}
```

The most basic mapping function just returns a specific field or value, e.g.,

```python
from operator import itemgetter

mapping = {
    'bank': 'BetterBank',
    'account': itemgetter('account_num'),
    'date': itemgetter('trx_date'),
    'amount': itemgetter('trx_amount')}
```

But more complex parsing is also possible, e.g.,

```python
mapping = {
    'account': lambda r: r['details'].split(':')[0],
    'date': lambda r: '%s/%s/%s' % (r['month'], r['day'], r['year']),
    'amount': lambda r: r['amount'] * 2}
```

### Required field attributes

attribute | description | default field | example
----------|-------------|---------------------|--------
`account`|transaction account|Account|BetterBank Checking
`date`|transaction date|Date|5/4/10
`amount`|transaction amount|Amount|$30.52

### Optional value attributes

attribute | description | default value
----------|-------------|---------------
`has_header`|does the csv file have a header row|True
`is_split`|does the csv file contain split (double entry) transactions|False
`currency`|the currency ISO code|USD
`delimiter`|the csv field delimiter|,

### Optional field attributes

attribute | description | default field | default value | example
----------|-------------|---------------|---------------|--------
`desc`|transaction description|Reference|n/a|shell station
`payee`|transaction payee|Description|n/a|Shell
`notes`|transaction notes|Notes|n/a|for gas
`check_num`|the check or transaction number|Row|n/a|2
`id`|transaction id|`check_num`|Num|n/a|531
`bank`|the bank name|n/a|`account`|Bank
`account_id`|transaction account id|n/a|hash of `account`|bb_checking
`type`|transaction account type|n/a|checking|savings
`balance`|account balance|n/a|n/a|$23.00
`class`|transaction class|n/a|n/a|travel

## Scripts

csv2ofx comes with a built in task manager `manage.py`.

### Setup

    pip install -r dev-requirements.txt

### Examples

*Run python linter and nose tests*

```bash
manage lint
manage test
```

## Contributing

Please mimic the coding style/conventions used in this repo. If you add new classes or functions, please add the appropriate doc blocks with examples. Also, make sure the python linter and nose tests pass.

Ready to contribute? Here's how:

1. Fork and clone.

```bash
git clone git@github.com:<your_username>/csv2ofx.git
cd csv2ofx
```

2. Setup a new [virtualenv](http://www.virtualenv.org/en/latest/index.html)

```bash
mkvirtualenv --no-site-packages csv2ofx
activate csv2ofx
python setup.py develop
pip install -r dev-requirements.txt
```

3. Create a branch for local development

```bash
git checkout -b name-of-your-bugfix-or-feature
```

4. Make your changes, run linter and tests, and submit a pull request through the GitHub website.

## License

csv2ofx is distributed under the [MIT License](http://opensource.org/licenses/MIT), the same as [tabutils](https://github.com/reubano/tabutils).
