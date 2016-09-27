import general as g
import numpy as np
from shapely.geometry import LineString, Point

def load_profile_data(config):
	g.verb(config.verbose, 'Loading data from file. {}'.format(config.f_data))
	data = np.loadtxt(config.f_data, delimiter=config.delimiter)
	
	g.verb(config.verbose, "Checking if number of slices is lower than actual length of data.")
	if config.num_of_slices < len(data):
		g.verb(config.verbose, "num_of_slices is set to a lower value"
		                       " than the total amount of data points."
		                       " Changing num_of_slices to '{}'"
		                       "".format(len(data)))
		
		config.num_of_slices = len(data)
	
	return data


def get_inter_points(config, circle, profile_data):
	g.verb(config.verbose, 'Finding Intersection between Circle and Profile')
	profile = LineString(profile_data)
	intsec_coor = list(circle.intersection(profile).bounds)
	
	if len(intsec_coor) == 0:
		exit("Error: Circle doesn't intersect the profile - please readjust circle coordinates in config file")
	
	if len(intsec_coor) != 4:
		exit("Error: Found more/less than two intersection coordinates\nNumber of intersections: {}"
		     "".format(len(intsec_coor)))
	
	return intsec_coor


def fetch_intsec_coords(config, intsec_coords):
	g.verb(config.verbose, "'Isolating section of profile: Length of element is correct.'")
	int1, int2 = (intsec_coords[0], intsec_coords[1]), (intsec_coords[2], intsec_coords[3])
	
	g.verb(config.verbose, "'Cross-checking intersection coordinates.'")
	if int1 == int2:
		g.verb(config.verbose,  "Error: Circle only intersects the profile in one "
	                            "place - please readjust circle coordinates "
	                            "in config file")
	
	return int1, int2


def linspace2d(profile, num_slices):
	num_slices = int(num_slices)
	array_x = profile[:, 0]
	array_y = profile[:, 1]
	num_slices -= 1
	
	n = num_slices / float(array_x.size - 1)
	
	x = np.arange(0, n * len(array_x), n)
	xx = np.arange((len(array_x) - 1) * n + 1)
	fin_array_x = np.interp(xx, x, array_x)
	
	y = np.arange(0, n * len(array_y), n)
	yy = np.arange((len(array_y) - 1) * n + 1)
	fin_array_y = np.interp(yy, y, array_y)
	## stack them
	fin_array = np.stack((fin_array_x, fin_array_y), axis=-1)
	return fin_array

def slice_array(profile, int1, int2, num_slices):
	## Iterate through array of 2d and find the coordinates the are the closest to the intersection points:
	boundary_list, first_time = [], True
	for index in range(len(profile) - 1):
		current, next = profile[index], profile[index + 1]
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
		exit("Error: Too many/not enough elements in boundary_list - please report this to "
		    "duan_uys@icloud.com\nNumber of Elements: {}"
		     "".format(len(boundary_list)))
	left_boundary, right_boundary = boundary_list[0], boundary_list[1]
	
	# Slice the data to contain the coordinates of the values from array2d
	slice_array2d = profile[left_boundary: right_boundary]
	
	# reconstruct slice_array2d to contain = num_of_elements
	slice_array2d = linspace2d(slice_array2d, num_slices)
	return slice_array2d
