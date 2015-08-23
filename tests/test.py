#!/usr/bin/env python

""" A script to test csv2ofx functionality """

import os
import sys

from hashlib import md5
from os import path as p
from tempfile import NamedTemporaryFile
from scripttest import TestFileEnvironment

parent_dir = p.abspath(p.dirname(p.dirname(__file__)))
example_dir = p.join(parent_dir, 'data', 'test')
check_dir = p.join(parent_dir, 'data', 'converted')


def main():
    """ Main method
    Returns 0 on success, 1 on failure
    """
    try:
        # setup
        env = TestFileEnvironment('.scripttest')
        tmpfile = NamedTemporaryFile(dir='%s' % parent_dir, delete=False)
        tmpname = tmpfile.name

        script = 'bin/csv2ofx --help'
        env.run('%s' % script, cwd='%s' % parent_dir)

        tests = [
            ('default.csv', 'default.qif', 'oq'),
            ('default.csv', 'default_w_splits.qif', 'oqS Category'),
            ('xero.csv', 'xero.qif', 'oqc Description -m xero'),
            ('mint.csv', 'mint.qif', 'oqS Category -m mint'),
            ('default.csv', 'default.ofx', 'o'),
            ('default.csv', 'default_w_splits.ofx', 'oS Category'),
            ('mint.csv', 'mint.ofx', 'oS Category -m mint'),
        ]

        for example_file, check_file, opts in tests:
            example = p.join(example_dir, example_file)
            check = p.join(check_dir, check_file)
            script = 'bin/csv2ofx -%s %s %s' % (opts, example, tmpname)
            env.run('%s' % script, cwd='%s' % parent_dir)
            myhash = md5(open(tmpname).read()).hexdigest()
            checkhash = md5(open(check).read()).hexdigest()
            assert myhash == checkhash
    except AssertionError:
        msg = "ERROR! Output from:\n\t%s\n" % ' '.join(script.split(' ')[:-1])
        msg += "doesn't match hash of\n\t%s\n" % check
        sys.stderr.write(msg)
    finally:
        os.unlink(tmpname)

    sys.exit(0)

if __name__ == '__main__':
    main()
