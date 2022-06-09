#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
csv2ofx.main
~~~~~~~~~~~~

Provides the primary ofx and qif conversion functions

Examples:
    literal blocks::

        python example_google.py

Attributes:
    ENCODING (str): Default file encoding.
"""
import time
import itertools as it
import traceback

from sys import stdin, stdout, exit
from importlib import import_module
from imp import find_module, load_module
from pkgutil import iter_modules
from operator import itemgetter
from os import path as p
from io import open
from datetime import datetime as dt
from argparse import RawTextHelpFormatter, ArgumentParser
from pprint import pprint
from math import inf

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

from builtins import *
from dateutil.parser import parse
from meza.io import read_csv, IterStringIO, write

from . import utils
from .ofx import OFX
from .qif import QIF


parser = ArgumentParser(  # pylint: disable=invalid-name
    description="description: csv2ofx converts a csv file to ofx and qif",
    prog="csv2ofx",
    usage="%(prog)s [options] <source> <dest>",
    formatter_class=RawTextHelpFormatter,
)

TYPES = ["CHECKING", "SAVINGS", "MONEYMRKT", "CREDITLINE", "Bank", "Cash"]
MAPPINGS = import_module("csv2ofx.mappings")
MODULES = tuple(itemgetter(1)(m) for m in iter_modules(MAPPINGS.__path__))


parser.add_argument(
    dest="source", nargs="?", help="the source csv file (default: stdin)"
)
parser.add_argument(dest="dest", nargs="?", help="the output file (default: stdout)")
parser.add_argument(
    "-a",
    "--account",
    metavar="TYPE",
    dest="account_type",
    choices=TYPES,
    help="default account type 'CHECKING' for OFX and 'Bank' for QIF.",
)
parser.add_argument(
    "-e",
    "--end",
    metavar="DATE",
    help="end date (default: today)",
    default=str(dt.now()),
)
parser.add_argument(
    "-l", "--language", help="the language (default: ENG)", default="ENG"
)
parser.add_argument("-s", "--start", metavar="DATE", help="the start date")
parser.add_argument(
    "-y",
    "--dayfirst",
    help="interpret the first value in ambiguous dates (e.g. 01/05/09) as the day",
    action="store_true",
    default=False,
)
parser.add_argument(
    "-m",
    "--mapping",
    metavar="MAPPING_NAME",
    help="the account mapping (default: default)",
    default="default",
    choices=MODULES,
)
parser.add_argument(
    "-x", "--custom", metavar="FILE_PATH", help="path to a custom mapping file"
)
parser.add_argument(
    "-c",
    "--collapse",
    metavar="FIELD_NAME",
    help=(
        "field used to combine transactions within a split for double entry "
        "statements"
    ),
)
parser.add_argument(
    "-C",
    "--chunksize",
    metavar="ROWS",
    type=int,
    default=2**14,
    help="number of rows to process at a time (default: 2 ** 14)",
)
parser.add_argument(
    "-r",
    "--first-row",
    metavar="ROWS",
    type=int,
    default=0,
    help="the first row to process (zero based)",
)
parser.add_argument(
    "-R",
    "--last-row",
    metavar="ROWS",
    type=int,
    default=inf,
    help="the last row to process (zero based, negative values count from the end)",
)
parser.add_argument(
    "-O",
    "--first-col",
    metavar="COLS",
    type=int,
    default=0,
    help="the first column to process (zero based)",
)
parser.add_argument(
    "-L",
    "--list-mappings",
    help="list the available mappings",
    action="store_true",
    default=False,
)
parser.add_argument(
    "-V", "--version", help="show version and exit", action="store_true", default=False
)
parser.add_argument(
    "-q",
    "--qif",
    help="enables 'QIF' output instead of 'OFX'",
    action="store_true",
    default=False,
)
parser.add_argument(
    "-o",
    "--overwrite",
    action="store_true",
    default=False,
    help="overwrite destination file if it exists",
)
parser.add_argument(
    "-D",
    "--server-date",
    metavar="DATE",
    help="OFX server date (default: source file mtime)",
)
parser.add_argument(
    "-E", "--encoding", default="utf-8", help="File encoding (default: utf-8)"
)
parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    default=False,
    help="display the options and arguments passed to the parser",
)
parser.add_argument(
    "-v", "--verbose", help="verbose output", action="store_true", default=False
)

args = parser.parse_args()  # pylint: disable=C0103


def run():  # noqa: C901
    """Parses the CLI options and runs the main program"""
    if args.debug:
        pprint(dict(args._get_kwargs()))  # pylint: disable=W0212
        exit(0)

    if args.version:
        from . import __version__ as version

        print("v%s" % version)
        exit(0)

    if args.list_mappings:
        print(", ".join(MODULES))
        exit(0)

    if args.custom:
        name = p.splitext(p.split(args.custom)[1])[0]
        found = find_module(name, [p.dirname(p.abspath(args.custom))])
        module = load_module(name, *found)
    else:
        module = import_module("csv2ofx.mappings.%s" % args.mapping)

    mapping = module.mapping

    okwargs = {
        "def_type": args.account_type or "Bank" if args.qif else "CHECKING",
        "start": parse(args.start, dayfirst=args.dayfirst) if args.start else None,
        "end": parse(args.end, dayfirst=args.dayfirst) if args.end else None,
    }

    cont = QIF(mapping, **okwargs) if args.qif else OFX(mapping, **okwargs)
    source = open(args.source, encoding=args.encoding) if args.source else stdin

    ckwargs = {
        "has_header": cont.has_header,
        "delimiter": mapping.get("delimiter", ","),
        "first_row": mapping.get("first_row", args.first_row),
        "last_row": mapping.get("last_row", args.last_row),
        "first_col": mapping.get("first_col", args.first_col),
    }

    try:
        records = read_csv(source, **ckwargs)
        groups = cont.gen_groups(records, args.chunksize)
        trxns = cont.gen_trxns(groups, args.collapse)
        cleaned_trxns = cont.clean_trxns(trxns)
        data = utils.gen_data(cleaned_trxns)
        body = cont.gen_body(data)

        if args.server_date:
            server_date = parse(args.server_date, dayfirst=args.dayfirst)
        else:
            try:
                mtime = p.getmtime(source.name)
            except (AttributeError, FileNotFoundError):
                mtime = time.time()

            server_date = dt.fromtimestamp(mtime)

        header = cont.header(date=server_date, language=args.language)
        footer = cont.footer(date=server_date)
        filtered = filter(None, [header, body, footer])
        content = it.chain.from_iterable(filtered)
        kwargs = {
            "overwrite": args.overwrite,
            "chunksize": args.chunksize,
            "encoding": args.encoding,
        }
    except Exception as err:  # pylint: disable=broad-except
        source.close()
        exit(err)

    dest = open(args.dest, "w", encoding=args.encoding) if args.dest else stdout

    try:
        res = write(dest, IterStringIO(content), **kwargs)
    except KeyError as err:
        msg = "Field %s is missing from file. Check `mapping` option." % err
    except TypeError as err:
        msg = "No data to write. %s. " % str(err)

        if args.collapse:
            msg += "Check `start` and `end` options."
        else:
            msg += "Try again with `-c` option."
    except ValueError as err:
        # csv2ofx called with no arguments or broken mapping
        msg = "Possible mapping problem: %s. " % str(err)
        parser.print_help()
    except Exception:  # pylint: disable=broad-except
        msg = 1
        traceback.print_exc()
    else:
        msg = 0 if res else "No data to write. Check `start` and `end` options."
    finally:
        exit(msg)
        source.close() if args.source else None
        dest.close() if args.dest else None


if __name__ == "__main__":
    run()
