import general_utils as General
import create_utils as Create
from shapely.geometry import LineString, Point, Polygon
import numpy as np

def formatCircleData(coordinates):
	"""Formated Circle data from Config File"""
	
	results = []
	coordinates = coordinates.replace(',', ' ')
	coordinates = coordinates.replace('(', '')
	coordinates = coordinates.replace(')', '')
	
	for element in coordinates.split():
		results.append(element)
	if len(results) > 4:
		General.raiseGeneralError("There are too many data points for your ellipse. Check config file")
	elif len(results) < 3:
		General.raiseGeneralError("There are too few data points for your circle/ellipse. Check config file.")
	else:
		return results


def arraylinspace1d(array_1d, num_elements):
	"""Returns 1D Numpy Array of given 1D Numpy Array with Expanded by num_elements"""
	
	array = array_1d
	num_elements -= 1
	n = num_elements / float(array.size - 1)
	
	x = np.arange(0, n * len(array), n)
	xx = np.arange((len(array) - 1) * n + 1)
	b = np.interp(xx, x, array)
	return b


def arraylinspace2d(array_2d, num_elements):
	"""Returns 2D Numpy Array of given 2D Numpy Array with Expanded by num_elements"""
	
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
		General.raiseGeneralError("Error: Too many/not enough elements in boundary_list - please report this to " \
		                          "duan_uys@icloud.com\nNumber of Elements: %d" % len(boundary_list))
	left_boundary, right_boundary = boundary_list[0], boundary_list[1]
	
	# Slice the data to contain the coordinates of the values from array2d
	slice_array2d = array2d[left_boundary: right_boundary]
	
	# reconstruct slice_array2d to contain = num_of_elements
	slice_array2d = arraylinspace2d(slice_array2d, num_of_elements)
	
	return slice_array2d


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


def trimCircleCoordinates(shapely_circle, profile_coords):
	err = "%s is not list object"
	circle_coords = list(Create.createNumpyArray(False, list(shapely_circle.coords)))
	if not isinstance(shapely_circle, LineString):
		raise TypeError(err % type(circle_coords))
	if not isinstance(profile_coords, list):
		raise TypeError(err % type(profile_coords))
	
	bound_list = intersec_circle_and_profile(False, shapely_circle, profile_coords)
	bx1, by1 = bound_list[0], bound_list[1]
	bx2, by2 = bound_list[2], bound_list[3]
	
	trimmedList = []
	for cx, cy in circle_coords:
		if cy <= by2:
			if bx1 <= cx <= bx2:
				trimmedList.append([cx, cy])
	
	trimmedList = np.array(trimmedList)
	
	return trimmedList


def loadProfileData(verbose, data_file, config):
	delimit = config.delimit
	num_of_slices = config.num_of_slices
	#### load data from file as numpy array
	General.verb(verbose, 'Load data from file as numpy array.')
	data = np.loadtxt(data_file, delimiter=delimit)
	####
	#
	#### Check to see if num_of_elements is lower than actual length of data:
	General.verb(verbose, 'Check to see if number of slices is lower than actual length of data.')
	if num_of_slices < len(data):
		General.verb(verbose, "You can not have num_of_elements set lower than your total amount of data points "
		                      "changing value to: num_of_slices = %d" % len(data))
		config.num_of_slices = len(data)
	return data


def intersec_circle_and_profile(verbose, shapely_circle, profile_data):
	"""Returns List Contain Intersection Coordinates Between Circle and Elevation Profile

	Arguments:
		verbose        -- Bool
		shapely_circle -- Circle Shapely Object
		profile_data   -- Numpy Array 2D"""
	
	General.verb(verbose, 'Finding Intersection between Circle and Profile')
	shapely_elevation_profile = LineString(profile_data)
	intersection_coordinates = list(shapely_circle.intersection(shapely_elevation_profile).bounds)
	
	if len(intersection_coordinates) == 0:
		General.raiseGeneralError(
			"Error: Circle doesn't intersect the profile - please readjust circle coordinates in config file")
	
	if len(intersection_coordinates) != 4:
		General.raiseGeneralError(
			"Error: Found more/less than two intersection coordinates\nNumber of intersections: %s" % \
			str(len(intersection_coordinates)))
	
	return intersection_coordinates


def fetchIntersecCoords(verbose, intersection_coordinates):
	"""Return Tuple of Coordinates of Intersection

	Arguments:
		verbose                     -- Bool
		intersection_coordinates    -- Tuple (x1, y1, x2, y2)"""
	
	General.verb(verbose, 'Isolating section of profile: Length of element is correct.')
	int1, int2 = (intersection_coordinates[0], intersection_coordinates[1]), (intersection_coordinates[2],
	                                                                          intersection_coordinates[3])
	# Check to see if intersection_1 and intersection_2 are the same. If they are that means the circle only intersects
	# the profile once.. not allowed
	General.verb(verbose, 'Cross-checking intersection coordinates.')
	if int1 == int2:
		General.raiseGeneralError(
			"Error: Circle only intersects the profile in one place - please readjust circle coordinates "
			"in config file")
	
	return int1, int2