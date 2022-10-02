#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
tests.test
~~~~~~~~~~

Provides scripttests to test csv2ofx CLI functionality.
"""

import sys

from difflib import unified_diff
from os import path as p
from io import StringIO, open
from timeit import default_timer as timer
from builtins import *

import pygogo as gogo

from scripttest import TestFileEnvironment

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


def main(script, tests, verbose=False, stop=True):
    """
    Returns 0 on success, 1 on failure
    """
    failures = 0
    logger = gogo.Gogo(__name__, verbose=verbose).logger
    short_script = p.basename(script)
    env = TestFileEnvironment(".scripttest")

    start = timer()
    for pos, test in enumerate(tests):
        num = pos + 1
        opts, arguments, expected = test
        joined_opts = " ".join(opts) if opts else ""
        joined_args = '"%s"' % '" "'.join(arguments) if arguments else ""
        command = "%s %s %s" % (script, joined_opts, joined_args)
        short_command = "%s %s %s" % (short_script, joined_opts, joined_args)
        result = env.run(command, cwd=PARENT_DIR, expect_stderr=True)
        output = result.stdout

        if isinstance(expected, bool):
            text = StringIO(output).read()
            outlines = [str(bool(text))]
            checklines = StringIO(str(expected)).readlines()
        elif p.isfile(expected):
            outlines = StringIO(output).readlines()

            with open(expected, encoding="utf-8") as f:
                checklines = f.readlines()
        else:
            outlines = StringIO(output).readlines()
            checklines = StringIO(expected).readlines()

        args = [checklines, list(filter_output(outlines))]
        kwargs = {"fromfile": "expected", "tofile": "got"}
        diffs = "".join(unified_diff(*args, **kwargs))

        if diffs:
            failures += 1
            msg = "ERROR! Output from test #%i:\n  %s\n" % (num, short_command)
            msg += "doesn't match:\n  %s\n" % expected
            msg += diffs if diffs else ""
        else:
            logger.debug(output)
            msg = "Scripttest #%i: %s ... ok" % (num, short_command)

        logger.info(msg)

        if stop and failures:
            break

    time = timer() - start
    logger.info("%s" % "-" * 70)
    end = "FAILED (failures=%i)" % failures if failures else "OK"
    logger.info("Ran %i scripttests in %0.3fs\n\n%s", num, time, end)
    sys.exit(failures)


if __name__ == "__main__":
    # pylint: disable=invalid-name
    csv2ofx = p.join(PARENT_DIR, "bin", "csv2ofx")

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
        (
            # N.B. input file obtained by pre-processing with
            #    bin/csvtrim ubs-ch-fr.csv > ubs-ch-fr_trimmed.csv
            ["-oq", "-m ubs-ch-fr"], "ubs-ch-fr_trimmed.csv", "ubs-ch-fr.qif"
        ),
        (
            ["-o", "-m outbank", "-e 20190301", SERVER_DATE],
            "outbank.csv",
            "outbank.ofx",
        ),
    ]

    main(csv2ofx, gen_test(PRE_TESTS))
