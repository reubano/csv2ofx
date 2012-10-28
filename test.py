#!/usr/bin/env python

""" A script to test csv2ofx functionality """

import os
import sys

from hashlib import md5
from tempfile import NamedTemporaryFile
from sys import exit
from scripttest import TestFileEnvironment

def main():
	try:
		env = TestFileEnvironment('.scripttest')
		dir = os.path.dirname(__file__)

		# test 1
		env.run('someprogram --help')

		# test 2
		example = os.path.join('examples', 'custom_example.csv')
		script = 'php csv2ofx.php -qm custom %s $' % example
		result = env.run('%s' % script, cwd='%s' % dir)
		file = NamedTemporaryFile(dir='%s' % dir, delete=False)
		name = file.name
		file.write('%s' % result.stdout)
		file.close()
		hash = md5(open(name).read()).hexdigest()
		os.unlink(name)
		assert hash == 'c15b2fc5fe2d0a35c4f76cb6c0297e8a'

	except Exception as err:
		sys.stderr.write('ERROR: %s\n' % str(err))

	exit(0)

if __name__ == '__main__': main()
