import general_utils as General
import calc_utils as Calc
import format_utils as Format
from shapely.geometry import LineString, Point
import numpy as np
import sys

def createNumpyArray(verbose, listObj, obj_name=''):
	"""Create Numpy Array from Object Type List

	Arguments:
		verbose  -- Bool
		listObj  -- List
		obj_name -- String"""
	
	General.verb(verbose, 'Converting %s coordinates into Numpy Array.' % str(obj_name))
	return np.array(list(listObj))


def createShapelyCircle(verbose, config):
	"""Create Shapely Circle Object

	Arguments:
		verbose -- Bool
		c_x     -- Int/Float
		c_y     -- Int/Float
		c_a     -- Int/Float
		c_b     -- Int/Float
		c_r     -- Int/Float (Deprecciated)"""
	c_x = config.c_x;
	c_y = config.c_y;
	c_a = config.c_a;
	c_b = config.c_b;
	c_r = config.c_r
	
	General.verb(verbose, 'Creating Shapely circle with ellipsoid data: (%s,%s,(%s,%s).' % (str(c_x), str(c_y),
	                                                                                        str(c_a), str(c_b)))
	try:
		General.verb(verbose, 'Trying to generate ellipsoid')
		if c_x is not None or c_y is not None or c_b is not None or c_a is not None:
			ellipse = generateEllipse(verbose, config)
			return LineString(ellipse)
		else:
			sys.exit("Error: c_x, c_y, c_a, c_b not set.. Report bug")
	except:
		General.verb(verbose, 'Ellipse failed: Reverting to perfect circle.')
		if c_x is not None or c_y is not None or c_r is not None:
			return Point(c_x, c_y).buffer(c_r).boundary
		else:
			sys.exit("Error: c_x, c_y, c_r not set.. Report bug")


def createShapelyLine(verbose, profile_data):
	"""Return Shapely MultLine Object of profile data

	Arguments:
		verbose -- Bool
		profile_data -- Numpy Array 2D / Nested Tuple ((x,y),(x,y))"""
	
	General.verb(verbose, "Creating Shapely Line with Elevation Profile")
	return LineString(profile_data)


def createSlicedElevProfile(verbose, elevation_profile, config, intersec_coord1, intersec_coord2):
	"""Return Numpy Array of reformed elevation data with num_of_slices data points. Essentially creating
	   sudo profile with many points

	   Arguments:
		   verbose           -- Bool
		   elevation_profile -- Numpy Array2D
		   num_of_slices     -- Int
		   intersec_coord1   -- Tuple (x,y)
		   intersec_coord2   -- Tuple (x,y)"""
	
	num_of_slices = config.num_of_slices
	General.verb(verbose, 'Creating Numpy array of sliced profile bounded within circle.')
	ep_profile = Format.arraylinspace2d(elevation_profile, num_of_slices)
	sliced_ep_profile = Format.slice_array(ep_profile, intersec_coord1, intersec_coord2, num_of_slices)
	return sliced_ep_profile


def generateEllipse(verbose, config):
	"""Return Numpy Array of Generated Coordinates of an Ellipsoid from Circle Data"""
	c_x = config.c_x;
	c_y = config.c_y;
	c_a = config.c_a;
	c_b = config.c_b
	
	General.verb(verbose, 'Creating Shapely circle with ellipsoid data: (%s,%s,(%s,%s).' % (str(c_x), str(c_y),
	                                                                                        str(c_a), str(c_b)))
	x_coords, y_coords = [], []
	degree = 0
	while degree <= 360:
		x = c_x + (c_a * np.cos(Calc.degree2rad(degree)))
		y = c_y + (c_b * np.sin(Calc.degree2rad(degree)))
		x_coords.append(x), y_coords.append(y)
		
		degree += 1
	
	x_coords, y_coords = np.array(x_coords), np.array(y_coords)
	xy_ellipse = np.stack((x_coords, y_coords), axis=-1)
	
	return xy_ellipse