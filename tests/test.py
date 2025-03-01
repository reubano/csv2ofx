#!/usr/bin/env python
# vim: sw=4:ts=4:expandtab

"""
tests.test
~~~~~~~~~~

Provides scripttests to test csv2ofx CLI functionality.
"""

import builtins
import itertools
import os
import shlex
import subprocess
import sys
from difflib import unified_diff
from io import StringIO
from os import path as p
from timeit import default_timer as timer

import pygogo as gogo

sys.path.append("../csv2ofx")

PARENT_DIR = p.abspath(p.dirname(p.dirname(__file__)))
EXAMPLE_DIR = p.join(PARENT_DIR, "data", "test")
CHECK_DIR = p.join(PARENT_DIR, "data", "converted")


def filter_output(outlines, debug_stmts=None):
    """Remove meza debugging statements"""
    def_stmts = ["File was opened in", "Decoding file with encoding"]
    debug_stmts = debug_stmts or def_stmts

    for line in outlines:
        if not any(stmt in line for stmt in debug_stmts):
            yield line


def flatten_opts(opts):
    return list(param for group in opts for param in shlex.split(group))


def main(tests, verbose=False, stop=True):
    """
    Returns 0 on success, 1 on failure
    """
    failures = 0
    logger = gogo.Gogo(__name__, verbose=verbose).logger

    start = timer()
    for pos, test in enumerate(tests):
        num = pos + 1
        opts, arguments, expected = test
        resolved_args = list(itertools.chain(flatten_opts(opts), arguments))
        command = ["csv2ofx"] + resolved_args
        short_command = f"csv2ofx {subprocess.list2cmdline(resolved_args)}"
        proc = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        output = proc.stdout

        if isinstance(expected, bool):
            text = StringIO(output).read()
            outlines = [str(bool(text))]
            checklines = StringIO(str(expected)).readlines()
        elif p.isfile(expected):
            outlines = StringIO(output).readlines()

            with builtins.open(expected, encoding="utf-8") as f:
                checklines = f.readlines()
        else:
            outlines = StringIO(output).readlines()
            checklines = StringIO(expected).readlines()

        args = [checklines, list(filter_output(outlines))]
        kwargs = {"fromfile": "expected", "tofile": "got"}
        diffs = "".join(unified_diff(*args, **kwargs))

        if diffs:
            failures += 1
            msg = f"ERROR! Output from test #{num}:\n  {short_command}\n"
            msg += f"doesn't match:\n  {expected}\n"
            msg += diffs if diffs else ""
        else:
            logger.debug(output)
            msg = f"Scripttest #{num}: {short_command} ... ok"

        logger.info(msg)

        if stop and failures:
            break

    time = timer() - start
    logger.info("{}".format("-") * 70)
    end = f"FAILED (failures={failures})" if failures else "OK"
    logger.info(f"Ran {num} scripttests in {time:.3f}s\n\n{end}")
    sys.exit(failures)


if __name__ == "__main__":

    def gen_test(raw):
        """Generate test arguments"""
        for opts, _in, _out in raw:
            if _in and _out:
                args = [p.join(EXAMPLE_DIR, _in)]
                yield (opts, args, p.join(CHECK_DIR, _out))
            else:
                yield (opts, _in, _out)

    MINT_ALT_OPTS = ["-oqs20150613", "-e20150614", "-m mint"]
    SERVER_DATE = "-D 20161031112908"
    SPLIT_OPTS = ["-o", "-m split_account", SERVER_DATE]
    PRE_TESTS = [
        (["--help"], [], True),
        (["-oq"], "default.csv", "default.qif"),
        (["-oq", "-m split_account"], "default.csv", "default_w_splits.qif"),
        (["-oqc Description", "-m xero"], "xero.csv", "xero.qif"),
        (["-oq", "-m mint"], "mint.csv", "mint.qif"),
        (["-oq", "-m mint_extra"], "mint_extra.csv", "mint_extra.qif"),
        (["-oq", "-m mint_headerless"], "mint_headerless.csv", "mint.qif"),
        (MINT_ALT_OPTS, "mint.csv", "mint_alt.qif"),
        (["-oe 20150908", SERVER_DATE], "default.csv", "default.ofx"),
        (SPLIT_OPTS, "default.csv", "default_w_splits.ofx"),
        (["-o", "-m mint", SERVER_DATE], "mint.csv", "mint.ofx"),
        (["-oq", "-m creditunion"], "creditunion.csv", "creditunion.qif"),
        (
            ["-o", "-m stripe", "-e", "20210505", SERVER_DATE],
            "stripe-default.csv",
            "stripe-default.ofx",
        ),
        (
            ["-o", "-m stripe", "-e", "20210505", SERVER_DATE],
            "stripe-all.csv",
            "stripe-all.ofx",
        ),
        (["-oq", "-m stripe"], "stripe-default.csv", "stripe-default.qif"),
        (["-oq", "-m stripe"], "stripe-all.csv", "stripe-all.qif"),
        (
            ["-E windows-1252", "-m gls", SERVER_DATE, "-e 20171111", "-o"],
            "gls.csv",
            "gls.ofx",
        ),
        (
            ["-o", "-m pcmastercard", "-e 20190120", SERVER_DATE],
            "pcmastercard.csv",
            "pcmastercard.ofx",
        ),
        # (
        #     # N.B. input file obtained by pre-processing with
        #     #    bin/csvtrim ubs-ch-fr.csv > ubs-ch-fr_trimmed.csv
        #     ["-oq", "-m ubs-ch-fr"], "ubs-ch-fr_trimmed.csv", "ubs-ch-fr.qif"
        # ),
        (
            ["-o", "-m ingesp", "-e 20221231", SERVER_DATE],
            "ingesp.csv",
            "ingesp.ofx",
        ),
        (
            ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
            "schwab-checking.csv",
            "schwab-checking.ofx",
        ),
        (
            ["-o", "-M", "-m schwabchecking", "-e 20220905", SERVER_DATE],
            "schwab-checking.csv",
            "schwab-checking-msmoney.ofx",
        ),
        (
            ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
            "schwab-checking-baltest-case1.csv",
            "schwab-checking-baltest-case1.ofx",
        ),
        (
            ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
            "schwab-checking-baltest-case2.csv",
            "schwab-checking-baltest-case2.ofx",
        ),
        (
            ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
            "schwab-checking-baltest-case3.csv",
            "schwab-checking-baltest-case3.ofx",
        ),
        (
            ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
            "schwab-checking-baltest-case4.csv",
            "schwab-checking-baltest-case4.ofx",
        ),
        (
            ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
            "schwab-checking-baltest-case5.csv",
            "schwab-checking-baltest-case5.ofx",
        ),
        (
            ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
            "schwab-checking-baltest-case6.csv",
            "schwab-checking-baltest-case6.ofx",
        ),
        (
            ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
            "schwab-checking-baltest-case7.csv",
            "schwab-checking-baltest-case7.ofx",
        ),
        (
            ["-o", "-m amazon", "-e 20230604", SERVER_DATE],
            "amazon.csv",
            "amazon.ofx",
        ),
        (
            ["-o", "-m payoneer", "-e 20220905", SERVER_DATE],
            "payoneer.csv",
            "payoneer.ofx",
        ),
    ]

    # for Amazon import; excludes transaction 3/3
    os.environ["AMAZON_EXCLUDE_CARDS"] = "9876"
    # clear the purchases account if set
    os.environ.pop("AMAZON_PURCHASES_ACCOUNT", None)
    assert "AMAZON_PURCHASES_ACCOUNT" not in os.environ

    main(gen_test(PRE_TESTS))
