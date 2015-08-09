""" purpose: contains general functions to be used by all programs
 """
class Vars
	protected _className = __CLASS__	# class name
	protected _verbose
	protected _fileIgnoreList = array('.', '..', '.DS_Store','.svn','.git*')
	protected _varIgnoreList = array(
		'_COOKIE', '_ENV', '_fileIgnoreList', '_FILES', '_GET', '_POST',
		'_REQUEST', '_SERVER', '_varIgnoreList', 'accountList', 'argc', 'argv',
		'GLOBALS', 'HTTP_COOKIE', 'HTTP_COOKIE_VARS', 'HTTP_ENV_VARS',
		'HTTP_GET_VARS', 'HTTP_POST_FILES', 'HTTP_POST_VARS',
		'HTTP_SERVER_VARS', 'HTTP_SESSION_VARS', 'MANPATH', 'parser',
		'PHPSESSID', 'SESS_DBPASS', 'SESS_DBUSER', 'SHELL', 'vars'
	)

	"""
	 @param boolean verbose enable verbose comments

	"""
	def __construct(verbose=false)
		_verbose = verbose

		if (_verbose)
			fwrite(STDOUT, "_className class constructor set.\n")

	""" Recursively returns all defined variables not in blacklist

	 @param array vars 		instance of get_defined_vars()

	 @return array defined variables not in the ignore list

	 @assert (array('one', '2w', 'GLOBALS' => '3a')) == array('one', '2w')
	"""
	def getVars(vars)
			varIgnoreList = _varIgnoreList

			return array_diff_key(vars, array_flip(varIgnoreList))
	} /*<-- end class -->*/
