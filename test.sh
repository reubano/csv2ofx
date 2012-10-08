#!/bin/sh
#
# A hook to disallow syntax errors to be committed
# by running a checker (lint, pep8, pylint...)  on them
#
# This is a pre-commit hook.
#
# To install this symlink it to $GIT_DIR/hooks, example:
#
# ln -s ../../git-tools/hooks/pre-commit .git/hooks/pre-commit

if [ $1 == 'php' ]; then
	PROGRAM=php
	EXT=php
	COMMAND='php -l'
else
	PROGRAM=python
	EXT=py
	COMMANDS="pep8\npylint --rcfile=standard.rc"
fi

if [ "$(echo -e test)" = test ]; then
	echo_e="echo -e"
else
	echo_e="echo"
fi

# necessary check for initial commit
if [ git rev-parse --verify HEAD >/dev/null 2>&1 ]; then
	against=HEAD
else
	# Initial commit: diff against an empty tree object
	against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

error=0
errors=""

if [ ! which "$PROGRAM" >/dev/null 2>&1 ]; then
	echo "$PROGRAM Syntax check failed:"
	echo "$PROGRAM binary does not exist or is not in path: $PROGRAM"
	exit 1
fi

# dash does not support $'\n':
IFS='
'
# get a list of staged files
for line in $(git diff-index --cached --full-index $against); do
	# split needed values
	sha=$(echo $line | cut -d' ' -f4)
	temp=$(echo $line | cut -d' ' -f5)
	status=$(echo $temp | cut -d'	' -f1)
	filename=$(echo $temp | cut -d'	' -f2)
	fileext=$(echo $filename | sed 's/^.*\.//')

	# only check files with proper extension
	if [ $fileext != $EXT ]; then
		continue
	fi

	# do not check deleted files
	if [ $status = "D" ]; then
		continue
	fi

	# check the staged file content for syntax errors
	# filter out everything other than parse errors with a grep below wether
	# printed to stdout or stderr

	result=$(git cat-file -p $sha | eval "$COMMAND" 2>&1)

	if [ $? -ne 0 ]; then
		error=1
		# Swap back in correct filenames
		errors=$(echo "$errors"; echo "$result" | sed -e "s@in - on@in $filename on@g")
	fi
done

unset IFS

if [ $error -eq 1 ]; then
	# 1. in cli, display_errors prints to standard output starting with
	#    "Parse error:" and log_errors prints to standard error starting with
	#    "PHP Parse error:" in php.ini.
	# 2. both are on by default therefore here we try to grep for one version
	#    and if that yields no results grep for the other version.
	# 3. it is possible to set both display_errors and log_errors to off. if
	#    this is done php will print the text "Errors parsing <file>" but will
	#    not say what the errors are. useful behavior, this.
	$echo_e "$errors" | grep "^Parse error:"

	if [ $? -ne 0 ]; then
		# match failed
		$echo_e "$errors" | grep "^PHP Parse error:"
	fi
	exit 1
fi
