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
		scriptdir = path.dirname(path.dirname(path.abspath('%s' % thisfile)))
		tmpfile = NamedTemporaryFile(dir='%s' % scriptdir, delete=False)
		tmpname = tmpfile.name

		# test 1
		script = 'php csv2ofx.php --help'
		env.run('%s' % script, cwd='%s' % scriptdir)

		# test 2
		example = os.path.join('examples', 'custom_example.csv')
		script = 'php csv2ofx.php -oqm custom %s %s' % (example, tmpname)
		env.run('%s' % script, cwd='%s' % scriptdir)
		myhash = md5(open(tmpname).read()).hexdigest()
		assert myhash == '82acc954a74d6dafaf3406603e677648'

		# test 3
		example = os.path.join('examples', 'xero_example.csv')
		script = 'php csv2ofx.php -oqm xero %s %s' % (example, tmpname)
		env.run('%s' % script, cwd='%s' % scriptdir)
		myhash = md5(open(tmpname).read()).hexdigest()
		assert myhash == 'f5585a5a64b320d0e0cabfc76a2ae4a7'

		# test 4
		example = os.path.join('examples', 'mint_example.csv')
		script = 'php csv2ofx.php -oqm mint %s %s' % (example, tmpname)
		env.run('%s' % script, cwd='%s' % scriptdir)
		myhash = md5(open(tmpname).read()).hexdigest()
		assert myhash == '177fb3afec2800956cd5074ade565886'

		# test 5
		example = os.path.join('examples', 'custom_example.csv')
		script = 'php csv2ofx.php -om custom %s %s' % (example, tmpname)
		env.run('%s' % script, cwd='%s' % scriptdir)
		myhash = md5(open(tmpname).read()).hexdigest()
		assert myhash == '2ab334e87c080941e413cc89701fb8a7'

		# test 6
		example = os.path.join('examples', 'custom_example.csv')
		script = 'php csv2ofx.php -otm custom %s %s' % (example, tmpname)
		env.run('%s' % script, cwd='%s' % scriptdir)
		myhash = md5(open(tmpname).read()).hexdigest()
		assert myhash == '402a8154573033193bc16d17fdf02f62'

		# cleanup
		os.unlink(tmpname)
	except Exception as err:
		sys.stderr.write('ERROR: %s on %s\n' % (str(err), myhash))
		os.unlink(tmpname)

	sys.exit(0)

if __name__ == '__main__':
	main()
