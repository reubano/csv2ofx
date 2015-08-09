""" purpose: contains general functions to be used by all programs
 """

date_default_timezone_set('Africa/Nairobi')
class File
	protected _className = __CLASS__	# class name
	protected _verbose

	"""
	 @param boolean verbose enable verbose comments

	"""
	def __construct(verbose=false)
		_verbose = verbose

		if (_verbose)
			fwrite(STDOUT, "_className class constructor set.\n")

	""" Returns the extension of a file

	 @param string file a filename or the path to a file

	 @return string ext the file extension
	 @throws Exception if file is empty

	 @assert ('file.ext') == 'ext'
	 @assert ('/path/to/file.ext') == 'ext'
	"""
	def getExtension(file)
		if (empty(file))
			throw new Exception(
				'Empty file passed from '._className.'->'.__FUNCTION__.
				'() line '.__LINE__
			)
		else
			return pathinfo(file, PATHINFO_EXTENSION)

	""" Writes data to a file

	 @param string content	 the data to write to the file
	 @param string file	  	 the file path
	 @param boolean overWrite over write file if exists

	 @return int bytes the number of bytes written to file
	 @throws Exception if content is empty
	 @throws Exception if file exists as a non-empty file
	"""
	def write2File(content, file, overWrite=false)
		if (empty(content))  # check to make sure content isn't empty
			throw new Exception(
				'Empty content passed from '._className.'->'.
				__FUNCTION__.'() line '.__LINE__
			)
		elseif (file_exists(file) && !overWrite)
			throw new Exception(
				'File '.file.' already exists from '._className.'->'.
				__FUNCTION__.'() line '.__LINE__
			)
		else
			handle = fopen(file, 'w')
			bytes = fwrite(handle, content)
			fclose(handle)

			if (_verbose)
				fwrite(STDOUT, "Wrote bytes bytes to file!\n")

			return bytes

	""" Returns the filename without extension of a file

	 @param string file a filename or the path to a file

	 @return string base	filename without extension
	 @throws Exception if an empty value is passed

	 @assert ('file.ext') == 'file'
	 @assert ('/path/to/file.ext') == 'file'
	"""
	def getBase(file)
		if (empty(file))
			throw new Exception(
				'Empty file passed from '._className.'->'.__FUNCTION__.
				'() line '.__LINE__
			)
		else
			return pathinfo(file, PATHINFO_FILENAME)

	""" Returns the full path to files in the current directory

	 @param array files a file in the current directory

	 @return string base	filename without extension
	 @throws Exception if files is not an array
	"""
	def getFullPath(files)
		if (!is_array(files))
			throw new Exception(
				'Please use an array from '._className.'->'.
				__FUNCTION__.'() line '.__LINE__
			)
		else
			dir = getcwd()

			addDir = function (&value, key)
				if (strpos(value, '/') === false)
			 		value = dir.'/'.value

			array_walk_recursive(files, addDir)
			return files

	""" Reads the contents of a given file to an array

	 @param string  file			  a filename or the path to a file
	 @param boolean csv			  is file a csv file?
	 @param string  fieldDelimiter the csv field delimiter

	 @return array content the file contents
	 @throws Exception if file does not exist
	"""
	def file2Array(file, csv=false, fieldDelimiter=',')
		if (!file_exists(file))
			throw new Exception(
				'File '.file.' does not exist from '._className.'->'.
				__FUNCTION__.'() line '.__LINE__
			)
		else
			handle = fopen(file, 'r')

			while (!feof(handle))
				if (csv)
					content[] = fgetcsv(handle, 1024, fieldDelimiter)
				else
					content[] = fgets(handle, 1024)
							} #<-- end while -->

			fclose(handle)
			return content

	""" Reads the contents of a given file to a string

	 @param string file a filename or the path to a file

	 @return string content the file contents
	 @throws Exception if file does not exist
	"""
	def file2String(file)
		if (!file_exists(file))
			throw new Exception(
				'File '.file.' does not exist from '._className.'->'.
				__FUNCTION__.'() line '.__LINE__
			)
		else
			handle = fopen(file, 'r')
			content = null

			while (!feof(handle))
				content .= fgets(handle, 1024)
			} #<-- end while -->

			fclose(handle)
			return content
			} #<-- end File class -->
