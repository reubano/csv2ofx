#!/bin/sh
#
# A script to disallow syntax errors to be committed
# by running a checker (lint, pep8, pylint...)  on them
#

# Redirect output to stderr.
exec 2>&1

# necessary check for initial commit
if [ git rev-parse --verify HEAD >/dev/null 2>&1 ]; then
	against=HEAD
else
	# Initial commit: diff against an empty tree object
	against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

# set Internal Field Separator to newline (dash does not support $'\n')
IFS='
'

# get a list of staged files
for LINE in $(git diff-index --cached --full-index $against); do
	# SHA=$(echo $line | cut -d' ' -f4)
	STATUS=$(echo $LINE | cut -d' ' -f5 | cut -d'	' -f1)
	FILENAME=$(echo $LINE | cut -d' ' -f5 | cut -d'	' -f2)
	FILEEXT=$(echo $FILENAME | sed 's/^.*\.//')

	# only check files with proper extension
	if [ $FILEEXT == 'php' ]; then
		PROGRAMS='php'
		COMMANDS='php -l'
	elif [ $FILEEXT == 'py' ]; then
		PROGRAMS=$'pep8\npylint'
		COMMANDS=$'pep8 --ignore=W191\npylint --rcfile=standard.rc -ry -fparseable'
	else
		continue
	fi

	for PROGRAM in $PROGRAMS; do
		test $(which $PROGRAM)

		if [ $? != 0 ]; then
			echo "$PROGRAM binary does not exist or is not in path"
			exit 1
		fi
	done

	# do not check deleted files
	if [ $STATUS == "D" ]; then
		continue
	fi

	# check the staged file content for syntax errors
	for COMMAND in $COMMANDS; do
 		RESULT=$(eval "$COMMAND $FILENAME")

		if [ $? != 0 ]; then
			echo "$COMMAND syntax check failed on $FILENAME"
			for LINE in $RESULT; do echo $LINE; done
			exit 1
		fi
	done
done
unset IFS

# If there are whitespace errors, print the offending file names and fail.
# exec git diff-index --check --cached $against --
