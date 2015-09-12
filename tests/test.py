#!/usr/bin/env python

""" A script to test csv2ofx functionality """

import os
import sys

from difflib import unified_diff
from os import path as p
from tempfile import NamedTemporaryFile
from scripttest import TestFileEnvironment
from timeit import default_timer as timer

parent_dir = p.abspath(p.dirname(p.dirname(__file__)))
example_dir = p.join(parent_dir, 'data', 'test')
check_dir = p.join(parent_dir, 'data', 'converted')


def main():
    """ Main method
    Returns 0 on success, 1 on failure
    """
    start = timer()
    script = 'bin/csv2ofx --help'
    env = TestFileEnvironment('.scripttest')
    tmpfile = NamedTemporaryFile(dir=parent_dir, delete=False)
    tmpname = tmpfile.name

    tests = [
        (2, 'default.csv', 'default.qif', 'oq'),
        (3, 'default.csv', 'default_w_splits.qif', 'oqS Category'),
        (4, 'xero.csv', 'xero.qif', 'oqc Description -m xero'),
        (5, 'mint.csv', 'mint.qif', 'oqS Category -m mint'),
        (6, 'default.csv', 'default.ofx', "oe '20150908'"),
        (7, 'default.csv', 'default_w_splits.ofx', 'oS Category'),
        (8, 'mint.csv', 'mint.ofx', 'oS Category -m mint'),
    ]

    try:
        env.run(script, cwd=parent_dir)
        print('\nScripttest: #1 ... ok')

        for test_num, example_filename, check_filename, opts in tests:
            example = p.join(example_dir, example_filename)
            check = p.join(check_dir, check_filename)
            checkfile = open(check)

            script = 'bin/csv2ofx -%s %s %s' % (opts, example, tmpname)
            env.run(script, cwd=parent_dir)
            args = [checkfile.readlines(), open(tmpname).readlines()]
            kwargs = {'fromfile': 'expected', 'tofile': 'got'}
            diffs = list(unified_diff(*args, **kwargs))

            if diffs:
                loc = ' '.join(script.split(' ')[:-1])
                msg = "ERROR from test #%i! Output:\n\t%s\n" % (test_num, loc)
                msg += "doesn't match hash of\n\t%s\n" % check
                sys.stderr.write(msg)
                sys.exit(''.join(diffs))
            else:
                print('Scripttest: #%i ... ok' % test_num)
    except Exception as e:
        sys.exit(e)
    else:
        time = timer() - start
        print('-----------------------------')
        print('Ran %i scripttests in %0.3fs\n\nOK' % (test_num, time))
        sys.exit(0)
    finally:
        checkfile.close
        os.unlink(tmpname)

if __name__ == '__main__':
    main()
