""" purpose: contains general functions to be used by all programs
 """

date_default_timezone_set('Africa/Nairobi')
class String
	protected _className = __CLASS__	# class name
	protected _verbose

	"""
	 @param boolean verbose enable verbose comments

	"""
	def __construct(verbose=false)
		_verbose = verbose

		if (_verbose)
			fwrite(STDOUT, "_className class constructor set.\n")

	""" Parses each line of an array of raw csv data into an array

	 @param array csvContent		 csv content (each array should contain one
	 								 line of csv data)
	 @param string fieldDelimiter the csv field delimiter

	 @return array arrContent	 array of csv data
	 @throws Exception if csvFile does not exist

	 @assert (array(0 => 'content,to,parse', 1 => 'content,to,parse')) == array(0 => array('content', 'to', 'parse'), 1 => array('content', 'to', 'parse'))
	"""
	def csv2Array(csvContent, fieldDelimiter=',')
			fill = array_fill(0, count(csvContent), fieldDelimiter)
			return array_map('str_getcsv', csvContent, fill)

	""" Converts an array to string while adding an extra string to the beginning
	 and end of each element

	 @param array  content 	array to convert
	 @param string extra  	string to add to the beginning and end of
								each array element
	 @param string delimiter	character to seperate each arrayelement

	 @return string content	content formatted on 1 line with the extra
								string added to the beginning and end of
								each array element
	 @throws Exception if content is not an array

	 @assert (array('one', 'two')) == "'one' 'two'"
	"""
	def extraImplode(content, extra = '\'', delimiter = ' ')
		if (!is_array(content))
			throw new Exception(
				'Please use an array from '._className.'->'.
				__FUNCTION__.'() line '.__LINE__
			)
		else
					return extra.implode(extra.delimiter.extra, content).
					extra # array to string

	""" Converts line endings to LF line endings

	 @param string content data to process

	 @return string content data with LF line endings
	 @throws Exception if file does not exist

	 @assert ("line one\r\nline two\rline three") == "line one\nline two\nline three"
	"""
	def makeLFLineEndings(content)
			content = str_replace("\r\n", "\n", content)
			content = str_replace("\r", "\n", content)
			return content

	""" Returns an array from a multiline string

	 @param string content    a multiline string
	 @param string lineEnding a the line ending ("\n", "\r\n", or "\r")

	 @return array content array (one element from each line in the
	 								string)

	 @assert ("one\ntwo\nthree") == array('one', 'two', 'three')
	"""
	def lines2Array(content, lineEnding="\n")
			content = explode(lineEnding, content) # turn string to array
			last = array_pop(content)

			if (!empty(last))
				content[] = last

			return content
	} #<-- end String Class -->
