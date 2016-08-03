import sys
import numpy as np
from matplotlib.widgets import Button
from shapely.geometry import LineString, Point, Polygon
import matplotlib.pyplot as plt


#### Basic Utils ####
def verb(v, string):
	if v:
		print '-> %s' % string


def hi(string):
	print string


def contains(character, string):
	equals = 0
	for char in string:
		if char == character:
			equals += 1
	if equals == 0:
		return False
	else:
		return True


def raiseGeneralError(arg):
	with open('err.log', "a") as errlog:
		errlog.write("Error: %s\n" % arg)
	raise StandardError(arg)


def isInt(value, variable):
	try:
		return int(value)
	except:
		return False


def isFloat(value, variable):
	try:
		return float(value)
	except:
		return False


def isString(value, variable):
	if not value.isdigit():
		return str(value)
	else:
		raiseGeneralError("Cannot contain numeric digits: %s = %s" % (variable, value))


def hasComma(value):
	content_list = []
	for char in value:
		content_list.append(char)
	if ',' in content_list:
		return True
	else:
		return False


def rad2degree(rad):
	return rad * 180. / np.pi


def degree2rad(degree):
	return degree * np.pi / 180.


def printslice(slice, vslice, percentage_status, sliced_ep_profile):
	try:
		if slice % vslice == 0:
			print 'Calculating Slice: %s %s' % (str(slice), display_percentage_status(percentage_status,
			                                                                          sliced_ep_profile.size,
			                                                                          slice))
	except:
		pass


def fetchIntersecCoords(verbose, intersection_coordinates):
	verb(verbose, 'Isolating section of profile: Length of element is correct.')
	int1, int2 = (intersection_coordinates[0], intersection_coordinates[1]), (intersection_coordinates[2],
	                                                                          intersection_coordinates[3])
	# Check to see if intersection_1 and intersection_2 are the same. If they are that means the circle only intersects
	# the profile once.. not allowed
	verb(verbose, 'Cross-checking intersection coordinates.')
	if int1 == int2:
		print "Error: Circle only intersects the profile in one place - please readjust circle coordinates in config file"
		sys.exit()

	return int1, int2


def createNumpyArray(verbose, listObj, obj_name=''):
	verb(verbose, 'Converting %s coordinates into Numpy Array.' % str(obj_name))
	return np.array(list(listObj))


#### /Basic Utils ####


#### Geometry Utils ####

def createShapelyCircle(verbose, c_x, c_y, c_a, c_b, c_r):
	verb(verbose, 'Creating Shapely circle with circle data.')
	try:
		verb(verbose, 'Trying to generate ellipsoid')
		if c_x is not None or c_y is not None or c_b is not None or c_a is not None:
			ellipse = generateEllipse(c_x, c_y, c_a, c_b)
			return LineString(ellipse)
		else:
			sys.exit("Error: c_x, c_y, c_a, c_b not set.. Report bug")
	except:
		verb(verbose, 'Ellipse failed: Reverting to perfect circle.')
		if c_x is not None or c_y is not None or c_r is not None:
			return Point(c_x, c_y).buffer(c_r).boundary
		else:
			sys.exit("Error: c_x, c_y, c_r not set.. Report bug")


def createShapelyLine(verbose, profile_data):
	verb(verbose, "Creating Shapely Line with Elevation Profile")
	return LineString(profile_data)


def createSlicedElevProfile(verbose, elevation_profile, num_of_slices, intersec_coord1, intersec_coord2):
	verb(verbose, 'Creating Numpy array of sliced profile bounded within circle.')
	ep_profile = arraylinspace2d(elevation_profile, num_of_slices)
	sliced_ep_profile = slice_array(ep_profile, intersec_coord1, intersec_coord2, num_of_slices)
	return sliced_ep_profile


def intersec_circle_and_profile(verbose, shapely_circle, profile_data):
	verb(verbose, 'Finding Intersection between Circle and Profile')
	shapely_elevation_profile = LineString(profile_data)
	intersection_coordinates = list(shapely_circle.intersection(shapely_elevation_profile).bounds)

	if len(intersection_coordinates) == 0:
		raiseGeneralError("Error: Circle doesn't intersect the profile - please readjust circle coordinates in config file")

	if len(intersection_coordinates) != 4:
		raiseGeneralError("Error: Found more/less than two intersection coordinates\nNumber of intersections: %s" % \
		      str(len(intersection_coordinates)))

	return intersection_coordinates


def isEllipse(value):
	for char in value:
		if char == "(" or char == ")":
			return True
	return False


def generateEllipse(c_x, c_y, c_a, c_b):
	x_coords, y_coords = [], []
	degree = 0
	while degree <= 360:
		x = c_x + (c_a * np.cos(degree2rad(degree)))
		y = c_y + (c_b * np.sin(degree2rad(degree)))
		x_coords.append(x), y_coords.append(y)

		degree += 1

	x_coords, y_coords = np.array(x_coords), np.array(y_coords)
	xy_ellipse = np.stack((x_coords, y_coords), axis=-1)

	return xy_ellipse


#### /Geometry Utils ####

#### Data Formatting Utils ####
def formatCircleData(coordinates):
	results = []

	coordinates = coordinates.replace(',', ' ')
	coordinates = coordinates.replace('(', '')
	coordinates = coordinates.replace(')', '')

	for element in coordinates.split():
		results.append(element)
	if len(results) > 4:
		raiseGeneralError("There are too many data points for your ellipse. Check config file")
	elif len(results) < 3:
		raiseGeneralError("There are too few data points for your circle/ellipse. Check config file.")
	else:
		return results


def arraylinspace1d(array_1d, num_elements):
	array = array_1d
	num_elements -= 1
	n = num_elements / float(array.size - 1)

	x = np.arange(0, n * len(array), n)
	xx = np.arange((len(array) - 1) * n + 1)
	b = np.interp(xx, x, array)
	return b


def arraylinspace2d(array_2d, num_elements):
	array_x = array_2d[:, 0]
	array_y = array_2d[:, 1]
	num_elements -= 1

	n = num_elements / float(array_x.size - 1)

	x = np.arange(0, n * len(array_x), n)
	xx = np.arange((len(array_x) - 1) * n + 1)
	fin_array_x = np.interp(xx, x, array_x)

	y = np.arange(0, n * len(array_y), n)
	yy = np.arange((len(array_y) - 1) * n + 1)
	fin_array_y = np.interp(yy, y, array_y)
	## stack them
	fin_array = np.stack((fin_array_x, fin_array_y), axis=-1)
	return fin_array


def slice_array(array2d, intersection_coord_1, intersection_coord_2, num_of_elements):
	"""
	:param array2d: Takes only numpy 2d array
	:param intersection_coord_1: a tuple, list of intersection coordinate
	:param intersection_coord_2: a tuple, list of intersection coordinate
	:return: returns a sliced numpy array within the boundaries of the given intersection coordinates
	"""
	int1, int2 = intersection_coord_1, intersection_coord_2
	## Iterate through array of 2d and find the coordinates the are the closest to the intersection points:
	boundary_list, first_time = [], True
	for index in range(len(array2d) - 1):
		current, next = array2d[index], array2d[index + 1]
		current_x, current_y = current[0], current[1]
		next_x, next_y = next[0], next[1]
		int1x, int1y, int2x, int2y = int1[0], int1[1], int2[0], int2[1]

		# Check to see if current and next elements are in between the coordinates of the intersections
		# store the results in a list


		if current_x < int1x < next_x or current_x < int2x < next_x:
			if not first_time:
				# boundary_list.append(current.tolist())
				boundary_list.append(index)
				first_time = False
			else:
				# boundary_list.append(next.tolist())
				boundary_list.append(index + 1)

	# Check to see if boundary_list is greater or less than 2: if so something went wrong
	if len(boundary_list) != 2:
		print "Error: Too many/not enough elements in boundary_list - please report this to " \
		      "duan_uys@icloud.com\nNumber of Elements: %d" % len(boundary_list)
		sys.exit()
	left_boundary, right_boundary = boundary_list[0], boundary_list[1]

	# Slice the data to contain the coordinates of the values from array2d
	slice_array2d = array2d[left_boundary: right_boundary]

	# reconstruct slice_array2d to contain = num_of_elements
	slice_array2d = arraylinspace2d(slice_array2d, num_of_elements)

	return slice_array2d


def display_percentage_status(percentage_status, size, slice):
	if percentage_status:
		num_elements = float(size / 2)
		perc = (slice / num_elements) * 100

		return " | (%d%%)" % perc
	else:
		return ''


#### /Formatting Utils ####


#### Calculation Utils ####



def FOS_calc(method, water_pore_pressure, mg, degree, effective_angle, cohesion, length):
	if method == 'bishop':
		denominator = mg * np.sin(degree)
		if water_pore_pressure == 0:
			numerator = (cohesion * length + (mg * np.cos(degree)) *
			             np.tan(effective_angle))
			numerator = (numerator / np.cos(degree) + (np.sin(degree) * np.tan(effective_angle) / 1.2))

		elif water_pore_pressure > 0:
			numerator = (cohesion * length + (mg * np.cos(degree) - water_pore_pressure * length * np.cos(degree)) *
			             np.tan(effective_angle))
			numerator = (numerator / np.cos(degree) + (np.sin(degree) * np.tan(effective_angle) / 1.2))
		else:
			raiseGeneralError("water_pore_pressure is a negative number!!!: %s" % water_pore_pressure)

		return numerator, denominator


	elif method == 'general':
		denominator = mg * np.sin(degree)
		if water_pore_pressure == 0:
			numerator = (mg * np.cos(degree)) * np.tan(effective_angle) + (cohesion * length)
		elif water_pore_pressure > 0:
			numerator = cohesion * length + (mg * np.cos(degree) - water_pore_pressure * length) * np.tan(
				effective_angle)
		else:
			raiseGeneralError("water_pore_pressure is a negative number!!!: %s" % water_pore_pressure)

		return numerator, denominator

	else:
		raiseGeneralError("No method was used.. aborting program")


def isolate_slice(index,
                  sliced_ep_profile,
                  shapely_circle,
                  bulk_density):
	buff = 10 ** 100
	current, next = sliced_ep_profile[index], sliced_ep_profile[index + 1]

	# create ambiguous line to be used for intersection calculation
	tempL_line = LineString([current, (current[0], current[1] - buff)])

	# find the intersection coord with the fake line and the arc
	intsec_arc1 = shapely_circle.intersection(tempL_line)

	# create ambiguous line to be used for intersection calculation
	tempR_line = LineString([next, (next[0], next[1] - buff)])

	# find the intersection coord with the fake right line and the arc
	intsec_arc2 = shapely_circle.intersection((tempR_line))

	# create actual polygon using the dimensions if and only if boundaries are set
	if not intsec_arc1.is_empty and not intsec_arc2.is_empty:
		# try to get the angle of the slope using trignometry

		int1_x, in1t_y = intsec_arc1.bounds[0], intsec_arc1.bounds[1]
		int2_x, in2t_y = intsec_arc2.bounds[2], intsec_arc2.bounds[3]

		prof1_x, prof1_y = current[0], current[1]
		prof2_x, prof2_y = next[0], next[1]

		# two calculations for hyptenuse 1) uses bottom of polygon -intersections with arc
		# 2) uses top of polygon - profile coordinates
		arc_hypotenuse = LineString([(int1_x, in1t_y), (int2_x, in2t_y)]).length
		prof_hypotenuse = LineString([(prof1_x, prof1_y), (prof2_x, prof2_y)]).length

		arc_tempH_line = LineString([(int2_x, in2t_y), (int2_x - buff, in2t_y)])
		prof_tempH_line = LineString([(prof1_x, prof1_y), (prof1_x + buff, prof1_y)])

		arc_temp_coor = tempL_line.intersection(arc_tempH_line)
		prof_temp_coor = tempL_line.intersection(prof_tempH_line)

		arc_base = LineString([arc_temp_coor, (int2_x, in2t_y)]).length
		prof_base = LineString([(prof1_x, prof1_y), prof_temp_coor]).length

		arc_length = LineString([(int1_x, in1t_y), (int2_x, in2t_y)]).length
		prof_length = LineString([(prof1_x, prof1_y), (prof2_x, prof2_y)]).length

		arc_degree = np.arccos(arc_base / arc_hypotenuse)
		prof_degree = np.arccos(prof_base / prof_hypotenuse)

		# For explanation on this piece of code:
		# https://github.com/Toblerity/Shapely/issues/21
		# Points and Coordinates are different things in Shapely
		# You have to work around that to use Points to construct
		# a Polygon
		curr, nx = Point(current), Point(next)
		int1, int2 = Point(int1_x, in1t_y), Point(int2_x, in2t_y)
		points = [int1, curr, nx, int2]
		coords = sum(map(list, (p.coords for p in points)), [])
		polygon = Polygon(coords)
		#
		# find the area of the polygon
		area = polygon.area
		# Find the weight of the slab:
		mg = area * bulk_density

		return arc_length, arc_degree, mg, prof_length, prof_degree


def FOS_Method(method,
               sliced_ep_profile,
               shapely_circle,
               bulk_density,
               soil_cohesion,
               effective_friction_angle,
               vslice,
               percentage_status,
               water_pore_pressure,
               verbose):
	"""
	:param method: a string stating the method of FOS calculation to be used
	:param sliced_ep_profile: a numpy array of the profile that is in the circle of interest
	:param shapely_circle:  a shapely object linestring that has the coorindates of the circle/ellipse
	:param bulk_density:    an integer for bulk_density of the soil
	:param soil_cohesion:   an integer for soil_cohesion of the soil
	:param effective_friction_angle: an integer in degrees of the effective angle of friction
	:param vslice: an integer that determines the modulo per batch of slices that should be outputed to the terminal
	:param percentage_status: a boolian expression to show percentage_status when completing stacks of slices
	:param water_pore_pressure: a positive integer expressing the water_pore_pore in kPa
	:param verbose: boolian expression if verbose statements should be printed to terminal

	:return:
		returns a single float number of the calculated factor of safety from the given parameters
	"""
	effective_angle = effective_friction_angle

	### Some checks to see if parameters passed are the right objects and set correctly ###
	if sliced_ep_profile.ndim != 2:
		raiseGeneralError("Numpy array is wrong size, %d, needs to be 2" % sliced_ep_profile.ndim)

	if not isinstance(shapely_circle, LineString):
		raiseGeneralError("Shapely_circle is somehow not a LineString object")

	if not isInt(bulk_density, 'bulk_density'):
		raiseGeneralError("Bulk Density is somehow not an integer")

	if not isInt(soil_cohesion, 'soil_cohesion'):
		raiseGeneralError("Soil Cohesion is somehow not an integer")

	if not isInt(effective_friction_angle, 'effective_friction_angle'):
		raiseGeneralError("Effective Friction Angle is somehow not an integer")

	if vslice <= 0:
		print '\r\nvslice can not be 0 or less: Setting default: 50.\r\n'
		vslice = 50

	if not isInt(water_pore_pressure, 'water_pore_pressure'):
		if int(water_pore_pressure) == 0:
			water_pore_pressure = 0
		else:
			raiseGeneralError("Water Pore Pressure is not an integer")
	elif water_pore_pressure < 0:
		raiseGeneralError("Water Pore Pressure cannot be a negative number: water_pore_pressure= %d" %
		                  water_pore_pressure)
	else:
		verb(verbose, "Water Pressure Set at %d" % water_pore_pressure)

	if percentage_status == 'on':
		percentage_status = True
	elif percentage_status == 'off':
		percentage_status = False
	else:
		raiseGeneralError("Percentage_status is not configured correctly: percentage_status = %s" % percentage_status)

	### Perform actual calculation of forces slice-by-slice
	numerator_list = []
	denominator_list = []
	errors = 0
	slice = 1
	for index in range(len(sliced_ep_profile) - 1):
		try:
			### Isolate variables of individual slice ##
			length, degree, mg, prof_length, prof_degree = isolate_slice(index, sliced_ep_profile,
			                                                             shapely_circle, bulk_density)
			effective_angle = degree2rad(effective_angle)

			# Calculate numerator and denominator of individual slice based on method
			numerator, denominator = FOS_calc(method,
			                                  water_pore_pressure,
			                                  mg,
			                                  degree,
			                                  effective_angle,
			                                  soil_cohesion,
			                                  length)

			numerator_list.append(numerator)
			denominator_list.append(denominator)

			# Print slices as they are calculated - turned off and on in config file.
			printslice(slice, vslice, percentage_status, sliced_ep_profile)
			slice += 1

			# Add results to lists that will be used to calculate the FOS in bulk
			numerator_list.append(numerator)
			denominator_list.append(denominator)
		except:
			errors += 1

	# convert calculated lists into numpy arrays
	numerator_list, denominator_list = np.array(numerator_list), np.array(denominator_list)
	success = 100 - (float(errors) / float(slice))
	error_result = "\nTotal number of errors encountered: %s\nPercent Success: %f%%" % (str(errors), (success))

	# calculate actual FOS from lists
	factor_of_safety = numerator_list.sum() / denominator_list.sum()

	# Finish up with so
	results = error_result + '\n\nMethod: %s\nCohesion: %d kPa\nEffective Friction Angle: %d\nBulk Density: %d ' \
	                         'Kg/m^3\nNumber of ' \
	                         'slices ' \
	                         'calculated: %d\nWater Pore Pressure: %d kPa\n\nFactor of Safety: %s\n' % (method.title(),
	                                                                                                    soil_cohesion,
	                                                                                                    effective_friction_angle,
	                                                                                                    bulk_density,
	                                                                                                    slice,
	                                                                                                    water_pore_pressure,
	                                                                                                    str(
		                                                                                                    factor_of_safety))

	f = open('results.log', 'w')
	f.write(results)
	f.close()
	return results


#### /Bishop Method ####

def perform_critical_slope_sim(verbose, config, data, fos):
	# find boundaries
	x = config.c_x
	y = config.c_y
	a, b = config.c_a, config.c_b
	r = config.c_r

	shapely_circle = createShapelyCircle(verbose, x, y, a, b, r)

	## find intersection coordinates of shapely_circle and profile data
	intersection_coordinates = intersec_circle_and_profile(verbose, shapely_circle, data)

	print intersection_coordinates, x, y, a, b, r
	try_loop = True

	while try_loop:
		try:
			shapely_circle = createShapelyCircle(verbose, x, y, a, b, r)
			intersection_coordinates = intersec_circle_and_profile(verbose, shapely_circle, data)
			x += 1
			print x
		except:
			try_loop = False
	exit()

	# created normal shapley object from raw profile data
	shapely_elevation_profile = createShapelyLine(verbose, data)

	## Using intersection coordinates isolate the section of profile that is within the circle.
	### Check to see if intersection_coordinates length is 4 elements.. if it isn't so that means for some reason
	# there are more or less than two intersection points in the profile - shouldn't really happen at all...
	int1, int2 = fetchIntersecCoords(verbose, intersection_coordinates)
	circle_coordinates = createNumpyArray(verbose, list(shapely_circle.coords), "Circle/Ellipse")
	elevation_profile = createNumpyArray(verbose, list(shapely_elevation_profile.coords), 'Profile Coordinates')

	# Create sliced array with boundaries from elevation_profile
	sliced_ep_profile = createSlicedElevProfile(verbose,
	                                            elevation_profile,
	                                            config.num_of_slices,
	                                            int1,
	                                            int2)

	### Perform actual calculation of forces slice-by-slice
	verb(verbose, 'Performing actual FOS calculation by Method: %s' % fos)

	results = ''
	if fos == 'general':
		results = FOS_Method(fos,
		                     sliced_ep_profile,
		                     shapely_circle,
		                     config.bulk_density,
		                     config.soil_cohesion,
		                     config.effective_friction_angle_soil,
		                     config.vslice,
		                     config.percentage_status,
		                     config.water_pore_pressure,
		                     verbose)

	elif fos == 'bishop':
		results = FOS_Method(fos,
		                     sliced_ep_profile,
		                     shapely_circle,
		                     config.bulk_density,
		                     config.soil_cohesion,
		                     config.effective_friction_angle_soil,
		                     config.vslice,
		                     config.percentage_status,
		                     config.water_pore_pressure,
		                     verbose)

	else:
		raiseGeneralError("Method: %s didn't execute" % fos)

	plt.scatter(circle_coordinates[:, 0], circle_coordinates[:, 1], color='red')
	ep_profile = arraylinspace2d(elevation_profile, config.num_of_slices)
	plt.scatter(ep_profile[:, 0], ep_profile[:, 1])
	plt.scatter(sliced_ep_profile[:, 0], sliced_ep_profile[:, 1], color='green')

	if config.save_figure == 'yes':
		verb(verbose, 'Saving result to figure.')
		plt.savefig('slope_profile.tif')

	print results


#### /Calculation Utils ####

#### GUI FUNCS ####
class Index(object):
	def abort_gui(self, event):
		sys.exit("Exitting")

	def cont_gui(self, event):
		print '-> Proceeding'
		plt.close('all')


def previewGeometery(show_figure, shapely_circle, profile_data):
	if show_figure == 'yes':
		circle_preview = np.array(list(shapely_circle.coords))
		plt.plot(profile_data[:, 0], profile_data[:, 1], color='red')
		plt.scatter(circle_preview[:, 0], circle_preview[:, 1])

		buttonopt = Index()
		quitax = plt.axes([0.7, 0.05, 0.1, 0.075])
		contax = plt.axes([0.81, 0.05, 0.1, 0.075])
		quit = Button(quitax, 'Quit')
		quit.on_clicked(buttonopt.abort_gui)
		cont = Button(contax, 'Continue')
		cont.on_clicked(buttonopt.cont_gui)
		plt.show()


#### /GUI FUNCS ####


#### CONFIG UTILS ####
class ReadConfig(object):
	### Initialize Variables ###
	delimit = ''
	soil_cohesion = -1
	bulk_density = -1
	num_of_slices = -1
	effective_friction_angle_soil = -1
	water_pore_pressure = -1
	show_figure = ''
	save_figure = ''
	circle_coordinates = ''
	vslice = 0
	percentage_status = ''
	verbose = ''
	perform_critical_slope = ''
	# Circle Data #
	c_x = 0.
	c_y = 0.
	# perfect circle #
	c_r = 0.
	# Ellipse #
	c_a = 0.
	c_b = 0.

	options_from_config = [
		'delimiter',  # 0
		'circle_coordinates',  # 1
		'soil_cohesion',  # 2
		'effective_friction_angle_soil',  # 3
		'bulk_density',  # 4
		'num_of_slices',  # 5
		'save_figure',  # 6
		'show_figure',  # 7
		'water_pore_pressure',  # 8
		'vslice',  # 9
		'percentage_status',  # 10
		'verbose',  # 11
		'perform_critical_slope',  # 12
	]

	def __init__(self, file_name):

		self.file_name = file_name

		# open file and read contents to store in variables
		with open(file_name) as f:
			content = f.readlines()
		line_num = 1
		for line in content:
			if not line.startswith('#') and not line.isspace():
				if not contains("=", line):
					raiseGeneralError("Could not find an '=' %d: %s" % (line_num, line))

				variable = line.split()[0]
				equal = line.split()[1]
				value = line.split()[2]
				if len(line.split()) > 3:
					raiseGeneralError("Wrong Syntax on line, %s: %s" % (line_num, line))
				if equal != '=':
					sys.exit("This shouldn't appear.Ever.")
				if not variable in str(self.options_from_config):
					raiseGeneralError("Couldn't find %s in options_from_config list" % variable)
				else:
					# print variable, equal, value
					if variable == self.options_from_config[0]:
						# delimeter - string
						self.delimit = isString(value, variable)

					elif variable == self.options_from_config[1]:
						# circle_coordinates
						if not hasComma(value):
							raiseGeneralError("Wrong Circle Coordinates - Check Config File")
						else:
							if isEllipse(value):
								value = formatCircleData(value)
								self.c_x = float(value[0])
								self.c_y = float(value[1])
								self.c_a = float(value[2])
								self.c_b = float(value[3])

							else:
								value = formatCircleData(value)
								self.c_x = float(value[0])
								self.c_y = float(value[1])
								self.c_r = float(value[2])

					elif variable == self.options_from_config[2]:
						# soil cohesion - float
						self.soil_cohesion = isFloat(value, variable)

					elif variable == self.options_from_config[3]:
						# internal friction angle - float
						self.effective_friction_angle_soil = isFloat(value, variable)

					elif variable == self.options_from_config[4]:
						# bulk density - float
						self.bulk_density = isFloat(value, variable)

					elif variable == self.options_from_config[5]:
						# number of slices - int
						self.num_of_slices = isInt(value, variable)

					elif variable == self.options_from_config[6]:
						# save figure - string
						self.save_figure = isString(value, variable)

					elif variable == self.options_from_config[7]:
						# show figure - string
						self.show_figure = isString(value, variable)

					elif variable == self.options_from_config[8]:
						# water pore pressure - float
						self.water_pore_pressure = isFloat(value, variable)

					elif variable == self.options_from_config[9]:
						# vslice bulk output - int
						self.vslice = isInt(value, variable)

					elif variable == self.options_from_config[10]:
						# Display percentage status - string
						self.percentage_status = isString(value, variable)

					elif variable == self.options_from_config[11]:
						# verbose switch - string
						self.verbose = isString(value, variable)

					elif variable == self.options_from_config[12]:
						# perform critical slope analysis
						self.perform_critical_slope = isString(value, variable)
					else:
						raiseGeneralError("Variable not found in options from config file: %s" % variable)

			line_num += 1


def loadProfileData(verbose, data_file, num_of_slices, delimit):
	#### load data from file as numpy array
	verb(verbose, 'Load data from file as numpy array.')
	data = np.loadtxt(data_file, delimiter=delimit)
	####
	#
	#### Check to see if num_of_elements is lower than actual length of data:
	verb(verbose, 'Check to see if number of slices is lower than actual length of data.')
	if num_of_slices < len(data):
		print "Error: You can't have num_of_elements set lower to your total amount of data points" \
		      "\n\nTotal Data Points: %s" \
		      "\nNum_of_slices: %s" % (str(len(data)), str(int(num_of_slices)))
		sys.exit()
	return data

	### /CONFIG UTILS ####
