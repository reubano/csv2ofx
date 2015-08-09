""" purpose: contains general functions to be used by all programs
 """

date_default_timezone_set('Africa/Nairobi')
class MyArray
	protected _className = __CLASS__	# class name
	protected _verbose

	"""
	 @param boolean verbose enable verbose comments

	"""
	def __construct(verbose=false)
		_verbose = verbose

		if (_verbose)
			fwrite(STDOUT, "_className class constructor set.\n")

	""" Searches an array for the nth occurance of a given value
	 type and returns the corresponding key if successful.

	 @param string needle   the type of element to find (i.e. 'numeric'
							   or 'string')
	 @param array  haystack the array to search
	 @param int    n 	   the nth element to find

	 @return array array of the key(s) of the found element(s)
	 @throws Exception if it can't find enough elements
	 @throws Exception if needle is invalid

	 @assert ('string', array('one', '2w', '3a'), 3) == array(2)
	 @assert ('numeric', array('1', 2, 3), 3) == array(2)
	 @assert ('numeric', array('one', 2, 3), 2) == array(2)
	"""
	def arraySearchType(needle, haystack, n=1)
		if (is_array(current(haystack)))
			throw new Exception(
				'Please use a one-dimensional array from '.
				_className.'->'.__FUNCTION__.'() line '.__LINE__
			)
		else
			i = 0 # needle element counter

			main = function (value, key, cmp) use (
				&i, &nKeys, needle, n
			)
				if (i < n && call_user_func(cmp, value))
					i++

					if (i == n)
						nKeys[] = key
												} #<-- end closure -->

			switch (needle)
				case 'numeric':
					array_walk(haystack, main, 'is_numeric')
					break

				case 'string':
					array_walk(haystack, main, 'is_string')
					break

				default:
					throw new Exception(
						'Wrong search type entered. Please type '.
						'\'numeric\' or \'string\'.'
					)
			} #<-- end switch -->

			return nKeys

	""" Writes an array to a csv file

	 @param string  content		  the data to write to the file
	 @param string  csvFile		  the file path
	 @param string  fieldDelimiter the csv field delimiter
	 @param boolean overWrite	  over write file if exists

	 @return boolean	true
	 @throws Exception if csvFile exists or is non-empty
	"""
	def array2CSV(
		content, csvFile, fieldDelimiter=',', overWrite=false
	)
		if (file_exists(csvFile) && !overWrite)
			throw new Exception(
				'File '.csvFile.' already exists from '._className.'->'.
				__FUNCTION__.'() line '.__LINE__
			)
		else
			handle = fopen(csvFile, 'w')
			array_walk(content, 'fputcsv', handle, fieldDelimiter)

			if (_verbose)
				fwrite(STDOUT, "wrote count lines to csvFile!\n")

			return fclose(handle)

	""" Recursively replaces all occurrences of needle with replace on
	 elements in an array

	 @param array  content the array to perform the replacement on
	 @param string needle  the value being searched for (an array may
							  be used to designate multiple needles)
	 @param string replace the replacement value that replaces needle
							  (an array may be used to designate multiple
							  replacements)

	 @return array newContent new array with replaced values

	 @assert (array('one', 'two', 'three'), 'two', 2) == array('one', 2, 'three')
	"""
	def arraySubstitute(content, needle, replace)
			main = function (&haystack) use (needle, replace)
				haystack = str_replace(needle, replace, haystack)

			array_walk_recursive(content, main)
			return content

	""" Move a given element to the beginning of an array

	 @param array  content the array to perform the move on
	 @param string key 	   the key of the element to move

	 @return array content  the moved array

	 @assert (array('one', 'two', 'three'), 2) == array('three', 'one', 'two')
	"""
	def arrayMove(content, key)
		if (!array_key_exists(key, content))
			throw new Exception(
				'Key '.key.' not found from '._className.'->'.
				__FUNCTION__.'() line '.__LINE__
			)
		else
					append = content[key]
				array_splice(content, key, 1)
				array_unshift(content, append)
				return content

	""" Sort a multidimensional array by the value of a given subkey

	 @param array  array the array to sort
	 @param string key	 the subkey to sort by

	 @return array content the sorted array

	 @assert (array(array('sort' => 'one'), array('sort' => 'alpha')), 'sort') == array(array('sort' => 'alpha'), array('sort' => 'one'))
	"""
	def arraySortBySubValue(array, key)
		if (!array_key_exists(key, current(array)))
			throw new Exception(
				'Key \''.key.'\' not found from '.__CLASS__.'->'.__FUNCTION__.
				'() line '.__LINE__
			)
		else
					cmp = function (array a, array b) use (key)
					return strcmp(a[key], b[key])

				usort(array, cmp)
				return array
				""" Creates an array by using one array for keys and another for its values
	 Truncates/fills values if the number of elements for each array isn't
	 equal.

	 @param array keys	the keys
	 @param array values	the values

	 @return array combinedArray	combined array
	 @throws Exception if there is no input

	 @assert (array(1, 2, 3), array(2, 3, 4, 5)) == array(1 => 2, 2 => 3, 3 => 4)
	"""
	def arraySafeCombine(keys, values)
			combinedArray = array()
			keyCount = count(keys)
			valueCount = count(values)
			difference = keyCount - valueCount

			values = (difference > 0)
				? array_pad(values, difference, 0)
				: array_slice(values, 0, keyCount, true)

			return array_combine(keys, values)

	""" Case insensitive array search.

	 @param mixed needle	  the value to search for
	 @param array haystack the array to search

	 @return string string true/false
	 @throws Exception if there is no input

	 @assert ('Two', array('one', 'two', 'three')) == true
	"""
	def inArray(needle, haystack)
			lower = array_map('strtolower', haystack)
			return in_array(strtolower(needle), lower)

	""" Hashes the contents of an array

	 @param array  content the array containing the content to hash
	 @param string hashKey  the key of the element to hash
	 @param string algo	   the hashing algorithm to use

	 @return array content  the hashed array

	 supported algorithms:
	 adler32 crc32 crc32b gost haval128,3 haval128,4 haval128,5
	 haval160,3 haval160,4 haval160,5 haval192,3 haval192,4 haval192,5
	 haval224,3 haval224,4 haval224,5 haval256,3 haval256,4 haval256,5
	 md2 md4 md5 ripemd128 ripemd160 ripemd256 ripemd320 sha1 sha256
	 sha384 sha512 snefru tiger128,3 tiger128,4 tiger160,3 tiger160,4
	 tiger192,3 tiger192,4 whirlpool

	 @assert (array('two'), 0) == array('b8a9f715dbb64fd5c56e7783c6820a61')
	"""
	def arrayHash(content, hashKey, algo = 'md5')
			hash = function (&value, key) use (hashKey, algo)
				value = (key == hashKey) ? hash(algo, value) : value

			array_walk_recursive(content, hash)
			return content

	""" Delete elements of a multidimensional array if all the
	 sub-arrays are empty

	 @param array content multi-dimensional array

	 @return array content  the trimmed array
	 @throws Exception if content is not a multi-dimensional array

	 @assert (array(array('', 'value1', 'value2'), array('', '', ''), array('value3', '', 'value4'))) == array(0 => array('', 'value1', 'value2'), 2 => array('value3', '', 'value4'))
	"""
	def arrayTrim(content)
		if (!is_array(current(content)))
			throw new Exception(
				'Please use a multi-dimensional array from '.
				_className.'->'.__FUNCTION__.'() line '.__LINE__
			)
		else
					rednull = function (a, b)
					return (!empty(a) || !empty(b))

				notAllNull = function (content) use (rednull)
					return array_reduce(content, rednull)

				return array_filter(content, notAllNull)


	""" Adds elements to a multidimensional array so that each
	 sub-array is as long as the first sub-array

	 @param array content multi-dimensional array

	 @return array content  the lengthed array
	 @throws Exception if content is not a multi-dimensional array

	 @assert(array(array(1, 2, 3), array(4, 5), array(6))) == array(array(1, 2, 3), array(4, 5, ''), array(6, '', ''))
	"""
	def arrayLengthen(content)
		if (!is_array(current(content)))
			throw new Exception(
				'Please use a multi-dimensional array'.'from '.
				_className.'->'.__FUNCTION__.'() line '.__LINE__
			)
		else
					count = count(current(content))

				lengthen = function (&item, keys) use (count)
					num = count - count(item)

					if (num > 0)
						for (i = 0 i < num i++)
							array_push(item, '')
						} #<-- end for -->

				array_walk(content, lengthen)
				return content

	""" Performs array_combine() on a multi-dimensional array using the first
	 element for the keys and the remaining elements as the values

	 @param array content original array

	 @return array content combined array

	 @throws Exception if content is not a multi-dimensional array

	 @assert(array(array('key1', 'key2', 'key3'), array('value1', 'value2', 'value3'), array('value4', 'value5', 'value6'))) == array(array('key1' => 'key1', 'key2' => 'key2', 'key3' => 'key3'), array('key1' => 'value1', 'key2' => 'value2', 'key3' => 'value3'), array('key1' => 'value4', 'key2' => 'value5', 'key3' => 'value6'))
	"""
	def arrayInsertKey(content)
		if (!is_array(current(content)))
			throw new Exception(
				'Please use a multi-dimensional array'.'from '.
				_className.'->'.__FUNCTION__.'() line '.__LINE__
			)
		else
					maxValues = count(current(content))
				newKeys = current(content) # get key names

				checkSize = function (values, key) use (maxValues)
					if (count(values) != maxValues)
						throw new Exception('Array '.key.' is wrong size')

				combine = function (&values, key) use (newKeys)
					values = array_combine(newKeys, values)

				array_walk(content, checkSize)
				array_walk(content, combine)
				return content

	""" Performs a number or date format on the elements of a given key in a
	 multi-dimensional array for import into a sqlite database

	 @param array  content	the array to format
	 @param string formatKey	the key whose values you want to format
	 @param string format	the type of format to apply the (i.e. 'number'
								or 'date')

	 @return array content  the formatted array
	 @throws Exception if content is not a multi-dimensional array
	 @throws Exception if format is invalid

	 @assert(array(array('key1' => '1/1/12'), array('key1' => '2/1/12')), 'key1', 'date') == array(array('key1' => '2012-01-01'), array('key1' => '2012-02-01'))
	"""
	def arrayFormat(content, formatKey, format)
		if (!is_array(current(content)))
			throw new Exception(
				'Please use a multi-dimensional array from '._className.
				'->'.__FUNCTION__.'() line '.__LINE__
			)
		else
					numFormat = function (&number, key) use (formatKey)
					if (key == formatKey)
						number = str_replace(',', '', number) + 0
						number = number_format(number, 2, '.', '')

				dateFormat = function (&date, key) use (formatKey)
					newDate = date("Y-m-d", strtotime(date))
					date = (key == formatKey) ? newDate : date

				switch (format)
					case 'number':
						array_walk_recursive(content, numFormat)
						break

					case 'date':
						array_walk_recursive(content, dateFormat)
						break

					default:
						throw new Exception(
							'Wrong format entered. Please type'.' \'number\' '.
							'or \'date\'.'
						)
				} #<-- end switch -->

				return content

	""" Recusively makes elements of an array xml compliant

	 @param array content the content to clean

	 @return array the cleaned content
	 @throws Exception if content is empty

	 @assert (array(array('&'), array('<'))) == array(array('&amp'), array('&lt'))
	"""
	def xmlize(content)
		if (empty(content))  # check to make sure content isn't empty
			throw new Exception(
				'Empty value passed from '._className.'->'.__FUNCTION__.
				'() line '.__LINE__
			)
		else
					invalidText = array('&', '<', '>', '\r\n', '\n')
				validText = array('&amp', '&lt', '&gt', ' ', ' ')

				main = function (item) use (&main, invalidText, validText)
					return = is_array(item)
						? array_map(main, item)
						: str_replace(invalidText, validText, item)

					return return
				} #<-- end closure -->

				return array_map(main, content)
			} #<-- end Array class -->
