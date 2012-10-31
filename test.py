#!/usr/bin/env python

""" A script to test csv2ofx functionality """

import os
import sys

from hashlib import md5
from tempfile import NamedTemporaryFile
from scripttest import TestFileEnvironment


def main():
	""" Main method
	Returns 0 on success, 1 on failure
	"""
	try:
		env = TestFileEnvironment('.scripttest')
		mydir = os.path.dirname(__file__)
		myfile = NamedTemporaryFile(dir='%s' % mydir, delete=False)
		name = myfile.name

		# test 1
		env.run('csv2ofx --help')

		# test 2
		example = os.path.join('examples', 'custom_example.csv')
		script = 'php csv2ofx.php -oqm custom %s %s' % (example, name)
		env.run('%s' % script, cwd='%s' % mydir)
		myhash = md5(open(name).read()).hexdigest()
		os.unlink(name)
		assert myhash == 'c15b2fc5fe2d0a35c4f76cb6c0297e8a'

	except Exception as err:
		sys.stderr.write('ERROR: %s\n' % str(err))

	sys.exit(0)

if __name__ == '__main__':
	main()
