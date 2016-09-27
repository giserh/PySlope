import numpy as np
import general as g
import format
from shapely.geometry import LineString
import matplotlib.pyplot as plt



def working_space(config, profile_data):
	circle = shapely_circle(config)
	intsec_coords = format.get_inter_points(config, circle, profile_data)
	profile = shapely_line(config, profile_data)
	int1, int2 = format.fetch_intsec_coords(config, intsec_coords)
	
	g.verb(config.verbose, "Converting ellipse coordinates into Numpy Array.")
	circ_coords = np.array(list(circle.coords))
	
	g.verb(config.verbose, "Converting profile coordinates into Numpy Array.")
	profile = np.array(list(profile.coords))
	sprofile = sliced_profile(config, profile, int1, int2)
	
	return sprofile, circle, circ_coords

def sliced_profile(config, profile, int1, int2):
	g.verb(config.verbose, "Creating Numpy array of sliced profile bounded within circle.")
	elevp = format.linspace2d(profile, config.num_of_slices)
	elevp = format.slice_array(elevp, int1, int2, config.num_of_slices)
	return elevp

def shapely_line(config, profile_data):
	g.verb(config.verbose, "Creating Shapely Line with Elevation Profile")
	return LineString(profile_data)
	
def shapely_circle(config):
	v = config.verbose
	x = config.ellipse_coordinates[0]
	y = config.ellipse_coordinates[1]
	a = config.ellipse_coordinates[2]
	b = config.ellipse_coordinates[3]
	
	g.verb(v, "Creating Shapely circle with ellipsoid data: {},{},{},{}."
	          "".format(x,y,a,b))
	
	circle = ellipse(config)
	return LineString(circle)
	
	
def ellipse(config):
	def _deg2rad(degree):
		return degree * np.pi / 180.
	
	if len(config.ellipse_coordinates) < 4:
		exit("Ellipse Coordinates are not formatted correctly."
		     " '{}'".format(config.ellipse_coordinates))
	
	v = config.verbose
	x = config.ellipse_coordinates[0]
	y = config.ellipse_coordinates[1]
	a = config.ellipse_coordinates[2]
	b = config.ellipse_coordinates[3]
	if len(config.ellipse_coordinates) == 5: c = config.ellipse_coordinates[4]
	else: c = None
	
	g.verb(v, "Generating ellipsoid coordinates: {},{},{},{}.".format(x,y,a,b))
	x_coords, y_coords = [], []
	degree = 0
	while degree <= 360:
		c_x = (a * np.cos(_deg2rad(degree)))
		c_y = (b * np.sin(_deg2rad(degree)))
		x_coords.append(c_x), y_coords.append(c_y)
		degree += 0.5
		
	x_coords, y_coords = np.array(x_coords), np.array(y_coords)
	
	if c is None:
		xy_ellipse = np.stack((x_coords + x, y_coords + y), axis=-1)
		return xy_ellipse
	
	x_coords = (x_coords*np.cos(_deg2rad(c))) - (y_coords * np.sin(_deg2rad(c)))
	y_coords = (x_coords * np.sin(_deg2rad(c))) + (y_coords * np.cos(_deg2rad(c)))
	xy_ellipse = np.stack((x_coords + x, y_coords +y), axis=-1)
	
	return xy_ellipse