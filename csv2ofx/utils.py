""" Searches an array for the nth occurrence of a given value
 type and returns the corresponding key if successful.

 @param string needle   the type of element to find (i.e. 'numeric'
							 or 'string')
 @param array  haystack the array to search

 @return array array of the key(s) of the found element(s)
 @throws Exception if it can't find enough elements
 @throws Exception if needle is invalid

 @assert ('string', array('one', '2w', '3a'), 3) == array(2)
 @assert ('numeric', array('1', 2, 3), 3) == array(2)
 @assert ('numeric', array('one', 2, 3), 2) == array(2)
"""
def array_search_type(needle, haystack, n=1):
	switch = {'numeric': 'real', 'string': 'upper'}
	func = lambda x: hasattr(item, switch[needle])
	return islice(ifilter(func, haystack), n, None)


""" Recursively replaces all occurrences of needle with replace on
 elements in an array

 @param array  content the array to perform the replacement on
 @param string needle  the value being searched for (an array may
							be used to designate multiple needles)
 @param string replace the replacement value that replaces needle
							(an array may be used to designate multiple
							replacements)

 @return array newContent new array with replaced values

 array_substitute([('one', 'two', 'three')], 'two', 2) == ('one', 2, 'three')
"""
def array_substitute(content, needle, replace):
	for item in content:
		if hasattr(item, 'upper'):
			yield replace if item == needle else item
		else:
			try:
				yield list(array_substitute(item, needle, replace))
			except TypeError:
				yield replace if item == needle else item


""" Recursively makes elements of an array xml compliant

 @param array content the content to clean

 @return array the cleaned content
 @throws Exception if content is empty

 @assert (array(array('&'), array('<'))) == array(array('&amp'), array('&lt'))
"""
def xmlize(content):
	replacements = [
		('&', '&amp'), ('>', '&gt'), ('<', '&lt'), ('\n', ' '), ('\r\n', ' ')]

	func = lambda x, y: x.replace(y[0], y[1])

	for item in content:
		if hasattr(item, 'upper'):
			yield reduce(func, replacements, item)
		else:
			try:
				yield list(xmlize(item, needle, replace))
			except TypeError:
				yield reduce(func, replacements, item)

""" Returns a number with ordinal suffix, e.g., 1st, 2nd, 3rd.

 @param integer num a number

 @return string ext a number with the ordinal suffix

 @assert (11) == '11th'
 @assert (132) == '132nd'
"""
def add_ordinal(num):
	switch = {1: 'st', 2: 'nd', 3: 'rd'}
	end = 'th' if (num % 100 in {11, 12, 13}) else switch.get(num % 10, 'th')
	return '%i%s' % (num, end)


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
def extraImplode(content, extra = '\'', delimiter = ' '):
	if (!is_array(content))
		throw new Exception(
			'Please use an array from '._className.'->'.
			__FUNCTION__.'() line '.__LINE__
		)
	else
				return extra.implode(extra.delimiter.extra, content).
				extra # array to string
