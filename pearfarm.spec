<?php

$spec = Pearfarm_PackageSpec::create(
	array(Pearfarm_PackageSpec::OPT_BASEDIR => dirname(__FILE__))
)
	->setName('csv2ofx')
	->setChannel('reubano.pearfarm.org')
	->setSummary('converts csv files to ofx and qif files')
	->setDescription('csv2ofx converts csv files to ofx and qif files and has built in support for csv source files from mint, yoodle, and xero')
	->setReleaseVersion('0.9.0')
	->setReleaseStability('beta')
	->setApiVersion('0.9.0')
	->setApiStability('beta')
	->setLicense(Pearfarm_PackageSpec::LICENSE_MIT)
	->setNotes('http://github.com/reubano/csv2ofx')
	->addMaintainer('lead', 'Reuben Cummings', 'reubano', 'reubano@gmail.com')
	->addGitFiles()
	->setDependsOnPHPVersion('5.3')
	->addPackageDependency('Console_CommandLine', 'pear.php.net')
	->addExcludeFiles(array('.gitignore', 'pearfarm.spec'))
	->addExecutable('csv2ofx')
	;