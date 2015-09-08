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
    test_num = 1
    script = 'bin/csv2ofx --help'
    env = TestFileEnvironment('.scripttest')
    tmpfile = NamedTemporaryFile(dir=parent_dir, delete=False)
    tmpname = tmpfile.name

    tests = [
        ('default.csv', 'default.qif', 'oq'),
        ('default.csv', 'default_w_splits.qif', 'oqS Category'),
        ('xero.csv', 'xero.qif', 'oqc Description -m xero'),
        ('mint.csv', 'mint.qif', 'oqS Category -m mint'),
        ('default.csv', 'default.ofx', 'o'),
        ('default.csv', 'default_w_splits.ofx', 'oS Category'),
        ('mint.csv', 'mint.ofx', 'oS Category -m mint'),
    ]

    env.run(script, cwd=parent_dir)
    print('\nScripttest: #%i ... ok' % test_num)
    test_num += 1

    for example_filename, check_filename, opts in tests:
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
            msg = "ERROR! Output from:\n\t%s\n" % loc
            msg += "doesn't match hash of\n\t%s\n" % check
            sys.stderr.write(msg)
            sys.exit(''.join(diffs))
        else:
            print('Scripttest: #%i ... ok' % test_num)
            test_num += 1

    checkfile.close
    os.unlink(tmpname)
    print('-----------------------------')
    print('Ran %i scripttests in %0.3fs\n\nOK' % (test_num, timer() - start))
    sys.exit(0)

if __name__ == '__main__':
    main()
