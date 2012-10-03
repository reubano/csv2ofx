# csv2ofx

## INTRODUCTION

[csv2ofx](http://github.com/reubano/csv2ofx) is a command line program that converts CSV files to OFX and QIF files for importing into GnuCash or similar financial accounting programs. csv2ofx has built in support for importing csv files from mint, yoodle, and xero. csv2ofx was ported from [mulicheng/csv2ofx](http://github.com/mulicheng/csv2ofx) and has been tested on the following configuration:

* MacOS X 10.7.4
* PHP 5.3.15
* Console_CommandLine 1.1.3

## REQUIREMENTS

csv2ofx requires the following programs in order to run properly:

* [PHP 5.3+](http://pear.php.net/manual/en/installation.php)
* [PEAR](http://us2.php.net/downloads.php)

## INSTALLATION
	
	sudo pear channel-discover reubano.github.com/pear
	sudo pear install reubano/csv2ofx

## USING csv2ofx
### Usage
	csv2ofx [options] <src_file> <dest_file>
	
### Examples

_normal usage_

	csv2ofx file.csv file.ofx

_stdout_

	csv2ofx ~/Downloads/transactions.csv $

_stdin_

	cat file.csv | csv2ofx -
		
_qif output_

	csv2ofx -q file.csv

_specify date range from one year ago to yesterday with qif output_

	csv2ofx -s '-1 year' -e yesterday -q file.csv

_use yoodle settings_

	csv2ofx -m yoodle file.csv
  
### Options
	  -A type, --account-type=type          account type to use if no match is
	                                        found, defaults to 'CHECKING' for
	                                        OFX and 'Bank' for QIF.
	  -c account(s), --collapse=account(s)  account(s) to summarize by date if
	                                        the transaction are recorded double
	                                        entry stlye (e.g. full data export
	                                        from xero.com or Quickbooks),
	                                        defaults to 'Accounts Receivable'
	  -C currency, --currency=currency      set currency, defaults to 'USD'
	  -d, --debug                           enables debug mode, displays the
	                                        options and arguments passed to the
	                                        parser
	  -D character, --delimiter=character   one character field delimiter,
	                                        defaults to ','
	  -e date, --end=date                   end date, defaults to today
	  -l lang, --language=lang              set language, defaults to 'ENG'
	  -o, --overwrite                       overwrite destination file if it
	                                        exists
	  -p name, --primary=name               primary account used to pay credit
	                                        cards, defaults to 'MITFCU
	                                        Checking'
	  -q, --qif                             enables 'QIF' output instead of
	                                        'OFX'
	  -s date, --start=date                 start date, defaults to '1/1/1900'
	  -m name, --mapping=name               mapping to use, defaults to 'mint'
	  -t, --transfer                        treats ofx transactions as
	                                        transfers from one account to
	                                        another (sets 'category' as the
	                                        destination account)
	  -v, --verbose                         verbose output
	  -V, --variables                       enables variable mode, displays the
	                                        value of all program variables
	  -h, --help                            show this help message and exit
	  --version                             show the program version and exit
	
### Arguments
	  src_file   the source csv file or data, enter '-' to read data from
	             standard input
	  dest_file  (optional) the destination file, enter '$' to print to
	             standard output, defaults to '.../csv2ofx/exports/...'

### Where does csv2ofx save files?

csv2ofx saves resultant qif and ofx files to the current directory. 

### Additional date format examples

	'10 September 2000'
	'08/10/00'
	'-2 years 1 week'
	'-1 month'
	'last friday'
	'next monday'

## CUSTOMIZATION

### Code modification

If you would like to import csv files that aren't from mint or yoodle, you will have to modify the code below in the csv2ofx.php file to match your csv header fields.

	default:
		$this->headAccount	= 'Field';
		$this->headAccountId= 'Field';
		$this->headDate 	= 'Field';
		$this->headTranType = 'Field';
		$this->headAmount 	= 'Field';
		$this->headDesc 	= 'Field';
		$this->headPayee 	= 'Field';
		$this->headNotes 	= 'Field';
		$this->headSplitAccount = 'Field';
		$this->headClass 	= 'Field';
		$this->headTranId 	= 'Field';
		$this->headCheckNum = 'Field';
		$this->split		= FALSE;

### Required variables

variable				| description                       
---------------------	| ------------- 
$this->headAccount		| account name                       
$this->headDate			| date the transaction was posted    
$this->headAmount		| amount of transaction              
$this->split			| is each split of the transaction on its own line? (true/false)

### Optional variables

variable				| description                       
---------------------	| ------------- 
$this->headDesc			| transaction description            
$this->headSplitAccount	| transaction split account name          
$this->headTranType		| type of transaction (credit/debit) 
$this->headNotes		| notes/memo                                                          
$this->headPayee		| transaction payee                  
$this->headClass		| transaction classification                                          
$this->headTranId		| unique transaction identifier

## LICENSE

csv2ofx is distributed under the [MIT License](http://opensource.org/licenses/mit-license.php), the same as [Console_CommandLine](http://pear.php.net/package/Console_CommandLine/) on which this program depends.
