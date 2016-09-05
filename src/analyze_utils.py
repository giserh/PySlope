def isInt(value):
	'''Tests if value is int type'''
	try:
		return int(value)
	except:
		return False


def isFloat(value):
	'''Tests if value is float type'''
	try:
		return float(value)
	except:
		return False


def isString(value, variable=''):
	'Tests if value contains non-digit characters'
	if not value.isdigit():
		return str(value)
	else:
		raise ValueError("Cannot contain numeric digits: %s = %s" % (variable, value))


def isEllipseFormat(value):
	'''
	Depreciated:
		Tests if value is in Ellipse Format
	'''
	for char in value:
		if char == "(" or char == ")":
			return True
	return False


def hasComma(value):
	'''Tests if value contains a comma ,'''
	content_list = []
	for char in value:
		content_list.append(char)
	if ',' in content_list:
		return True
	else:
		return False


def isCircle(a, b):
	'''Tests wetheer coordinates are circle or ellipse'''
	if a == b:
		return True
	else:
		return False


def contains(character, string):
	'''Tests if specific character is found in string'''
	equals = 0
	for char in string:
		if char == character:
			equals += 1
	if equals == 0:
		return False
	else:
		return True