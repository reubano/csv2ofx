#!/usr/bin/env python

""" A script to test csv2ofx functionality """

import inspect
import os
import sys

from hashlib import md5
from os import path
from tempfile import NamedTemporaryFile
from scripttest import TestFileEnvironment


def main():
	""" Main method
	Returns 0 on success, 1 on failure
	"""
	try:
		# setup
		env = TestFileEnvironment('.scripttest')
		thisfile = inspect.getfile(inspect.currentframe())
		thisdir = path.dirname(path.abspath('%s' % thisfile))
		tmpfile = NamedTemporaryFile(dir='%s' % thisdir, delete=False)
		tmpname = tmpfile.name

		# test 1
		script = 'php csv2ofx.php --help'
		env.run('%s' % script, cwd='%s' % thisdir)

		# test 2
		example = os.path.join('examples', 'custom_example.csv')
		script = 'php csv2ofx.php -oqm custom %s %s' % (example, tmpname)
		env.run('%s' % script, cwd='%s' % thisdir)
		myhash = md5(open(tmpname).read()).hexdigest()
		os.unlink(tmpname)
		assert myhash == 'c15b2fc5fe2d0a35c4f76cb6c0297e8a'

		# test 3
		example = os.path.join('examples', 'xero_example.csv')
		script = 'php csv2ofx.php -oqm xero %s %s' % (example, tmpname)
		env.run('%s' % script, cwd='%s' % thisdir)
		myhash = md5(open(tmpname).read()).hexdigest()
		os.unlink(tmpname)
		assert myhash == 'c15b2fc5fe2d0a35c4f76cb6c0297e8a'

	except Exception as err:
		sys.stderr.write('ERROR: %s\n' % str(err))

	sys.exit(0)

if __name__ == '__main__':
	main()
