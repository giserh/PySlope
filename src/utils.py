import matplotlib.pyplot as plt
import sys
from matplotlib.widgets import Button
import numpy as np
from shapely.geometry import Point, Polygon, LineString


class Index(object):
	def abort_gui(self, event):
		sys.exit("Exitting")
	
	def cont_gui(self, event):
		print '-> Proceeding'
		plt.close('all')


class General(object):
	@staticmethod
	def verb(v, string):
		'''Prints verbose string to terminal'''
		if v:
			print '-> %s' % string
	
	@staticmethod
	def raiseGeneralError(arg):
		'''Raises standard error'''
		raise StandardError(arg)
	
	@staticmethod
	def printslice(verbose, slice, vslice, percentage_status, sliced_ep_profile):
		"""Print Computed Slices in Batches

		Arguments:
			verbose             -- Bool
			slice               -- Int, Current Slice Value
			vslice              -- Int, Slice Value To Print - configured in config file
			percentage_status   -- Bool
			sliced_ep_profile   -- Numpy Array - Elevation Profile"""
		
		try:
			if slice % vslice == 0 and verbose:
				print 'Calculating Slice: %s %s' % (str(slice), General.display_percentage_status(percentage_status,
				                                                                                  sliced_ep_profile.size,
				                                                                                  slice))
		except:
			pass
	
	@staticmethod
	def printResults(verbose, error_result, method, soil_cohesion, effective_friction_angle, bulk_density, slice,
	                 water_pore_pressure, factor_of_safety):
		"""Print Computed Results

		Arguments:
			verbose                  -- Bool
			error_result             -- Float
			method                   -- String
			soil_cohesion            -- Int, Float
			effective_friction_angle -- Int
			bulk_density             -- Int
			slice                    -- Int
			water_pore_pressure      -- Int
			factor_of_safety         -- string"""
		
		if verbose:
			results = error_result + '\n\nMethod: %s\nCohesion: %d kPa\nEffective Friction Angle: %d\nBulk Density: %d ' \
			                         'Kg/m^3\nNumber of ' \
			                         'slices ' \
			                         'calculated: %d\nWater Pore Pressure: %d kPa\n\nFactor of Safety: %s\n' % (
				                         method.title(),
				                         soil_cohesion,
				                         effective_friction_angle,
				                         bulk_density,
				                         slice,
				                         water_pore_pressure,
				                         str(
					                         factor_of_safety))
		else:
			results = "Factor of Safety: %s" % str(factor_of_safety)
		
		with open('results.txt', 'w') as f:
			f.write(results)
		print results
	
	@staticmethod
	def previewGeometery(verbose, config, profile_data):
		if config.show_figure == 'yes':
			circle_preview = Create.generateEllipse(verbose, config)
			plt.plot(profile_data[:, 0], profile_data[:, 1], color='red')
			plt.grid(True)
			plt.axes().set_aspect('equal', 'datalim')
			plt.xlabel("Spatial Distance - X")
			plt.ylabel("Height of Profile - Y")
			plt.scatter(circle_preview[:, 0], circle_preview[:, 1])
			
			
			buttonopt = Index()
			quitax = plt.axes([0.7, 0.05, 0.1, 0.075])
			contax = plt.axes([0.81, 0.05, 0.1, 0.075])
			quit = Button(quitax, 'Quit')
			quit.on_clicked(buttonopt.abort_gui)
			cont = Button(contax, 'Continue')
			cont.on_clicked(buttonopt.cont_gui)
			plt.show()
	
	@staticmethod
	def display_percentage_status(percentage_status, size, slice):
		"""Returns String of Percentage Status"""
		if percentage_status:
			num_elements = float(size / 2)
			perc = (slice / num_elements) * 100
			
			return " | (%d%%)" % perc
		else:
			return ''


class Analysis(object):
	@staticmethod
	def isInt(value):
		'''Tests if value is int type'''
		try:
			return int(value)
		except:
			return False
	
	@staticmethod
	def isFloat(value):
		'''Tests if value is float type'''
		try:
			return float(value)
		except:
			return False
	
	@staticmethod
	def isString(value, variable=''):
		'Tests if value contains non-digit characters'
		if not value.isdigit():
			return str(value)
		else:
			raise ValueError("Cannot contain numeric digits: %s = %s" % (variable, value))
	
	@staticmethod
	def isEllipseFormat(value):
		'''
		Depreciated:
			Tests if value is in Ellipse Format
		'''
		for char in value:
			if char == "(" or char == ")":
				return True
		return False
	
	@staticmethod
	def hasComma(value):
		'''Tests if value contains a comma ,'''
		content_list = []
		for char in value:
			content_list.append(char)
		if ',' in content_list:
			return True
		else:
			return False
	
	@staticmethod
	def isCircle(a, b):
		'''Tests wetheer coordinates are circle or ellipse'''
		if a == b:
			return True
		else:
			return False
	
	@staticmethod
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


class Create(object):
	@staticmethod
	def createNumpyArray(verbose, listObj, obj_name=''):
		"""Create Numpy Array from Object Type List

		Arguments:
			verbose  -- Bool
			listObj  -- List
			obj_name -- String"""
		
		General.verb(verbose, 'Converting %s coordinates into Numpy Array.' % str(obj_name))
		return np.array(list(listObj))
	
	@staticmethod
	def createShapelyCircle(verbose, config):
		"""Create Shapely Circle Object

		Arguments:
			verbose -- Bool
			c_x     -- Int/Float
			c_y     -- Int/Float
			c_a     -- Int/Float
			c_b     -- Int/Float
			c_r     -- Int/Float (Deprecciated)"""
		c_x = config.c_x; c_y = config.c_y; c_a = config.c_a; c_b = config.c_b; c_r = config.c_r
		
		General.verb(verbose, 'Creating Shapely circle with ellipsoid data: (%s,%s,(%s,%s).' % (str(c_x), str(c_y),
		                                                                                        str(c_a), str(c_b)))
		try:
			General.verb(verbose, 'Trying to generate ellipsoid')
			if c_x is not None or c_y is not None or c_b is not None or c_a is not None:
				ellipse = Create.generateEllipse(verbose, config)
				return LineString(ellipse)
			else:
				sys.exit("Error: c_x, c_y, c_a, c_b not set.. Report bug")
		except:
			General.verb(verbose, 'Ellipse failed: Reverting to perfect circle.')
			if c_x is not None or c_y is not None or c_r is not None:
				return Point(c_x, c_y).buffer(c_r).boundary
			else:
				sys.exit("Error: c_x, c_y, c_r not set.. Report bug")
	
	@staticmethod
	def createShapelyLine(verbose, profile_data):
		"""Return Shapely MultLine Object of profile data

		Arguments:
			verbose -- Bool
			profile_data -- Numpy Array 2D / Nested Tuple ((x,y),(x,y))"""
		
		General.verb(verbose, "Creating Shapely Line with Elevation Profile")
		return LineString(profile_data)
	
	@staticmethod
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
	
	@staticmethod
	def generateEllipse(verbose, config):
		"""Return Numpy Array of Generated Coordinates of an Ellipsoid from Circle Data"""
		c_x = config.c_x; c_y = config.c_y; c_a = config.c_a; c_b = config.c_b
		
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


class Format(object):
	@staticmethod
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
	
	@staticmethod
	def arraylinspace1d(array_1d, num_elements):
		"""Returns 1D Numpy Array of given 1D Numpy Array with Expanded by num_elements"""
		
		array = array_1d
		num_elements -= 1
		n = num_elements / float(array.size - 1)
		
		x = np.arange(0, n * len(array), n)
		xx = np.arange((len(array) - 1) * n + 1)
		b = np.interp(xx, x, array)
		return b
	
	@staticmethod
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
	
	@staticmethod
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
		slice_array2d = Format.arraylinspace2d(slice_array2d, num_of_elements)
		
		return slice_array2d
	
	@staticmethod
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
	
	@staticmethod
	def trimCircleCoordinates(shapely_circle, profile_coords):
		err = "%s is not list object"
		circle_coords = list(Create.createNumpyArray(False, list(shapely_circle.coords)))
		if not isinstance(shapely_circle, LineString):
			raise TypeError(err % type(circle_coords))
		if not isinstance(profile_coords, list):
			raise TypeError(err % type(profile_coords))
		
		bound_list = Format.intersec_circle_and_profile(False, shapely_circle, profile_coords)
		bx1, by1 = bound_list[0], bound_list[1]
		bx2, by2 = bound_list[2], bound_list[3]
		
		trimmedList = []
		for cx, cy in circle_coords:
			if cy <= by2:
				if bx1 <= cx <= bx2:
					trimmedList.append([cx, cy])
		
		trimmedList = np.array(trimmedList)
		
		return trimmedList
	
	@staticmethod
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
			General.verb(verbose, "You can not have num_of_elements set lower than your total amount of data points"
			                      "changing value to: %d" % len(data))
			config.num_of_slices = len(data)
		return data
	
	@staticmethod
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
	
	@staticmethod
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


class Calc(object):
	@staticmethod
	def rad2degree(rad):
		'''Converts radian to degree'''
		return rad * 180. / np.pi
	
	@staticmethod
	def degree2rad(degree):
		'''Converts degree to radian'''
		return degree * np.pi / 180.
	
	@staticmethod
	def FOS_calc(method, water_pore_pressure, mg, degree, effective_angle, cohesion, length, FOS=1.2):
		numerator = None
		
		if method == 'bishop':
			denominator = mg * np.sin(degree)
			if water_pore_pressure == 0:
				numerator = (cohesion * length + (mg * np.cos(degree)) *
				             np.tan(effective_angle))
				numerator = (numerator / np.cos(degree) + (np.sin(degree) * np.tan(effective_angle) / FOS))
			
			elif water_pore_pressure > 0:
				numerator = (cohesion * length + (mg * np.cos(degree) - water_pore_pressure * length * np.cos(degree)) *
				             np.tan(effective_angle))
				numerator = (numerator / np.cos(degree) + (np.sin(degree) * np.tan(effective_angle) / FOS))
			else:
				General.raiseGeneralError("water_pore_pressure is a negative number!!!: %s" % water_pore_pressure)
			
			return numerator, denominator
		
		
		elif method == 'general':
			denominator = mg * np.sin(degree)
			if water_pore_pressure == 0:
				numerator = (mg * np.cos(degree)) * np.tan(effective_angle) + (cohesion * length)
			elif water_pore_pressure > 0:
				numerator = cohesion * length + (mg * np.cos(degree) - water_pore_pressure * length) * np.tan(
					effective_angle)
			else:
				General.raiseGeneralError("water_pore_pressure is a negative number!!!: %s" % water_pore_pressure)
			
			return numerator, denominator
		
		else:
			General.raiseGeneralError("No method was used.. aborting program")
	
	@staticmethod
	def sim_calc(verbose, x, y, a, b, r, data, config, fos, FOS=1.2):
		shapely_circle = Create.createShapelyCircle(False, config)
		intersection_coordinates = Format.intersec_circle_and_profile(False, shapely_circle, data)
		shapely_elevation_profile = Create.createShapelyLine(verbose, data)
		int1, int2 = Format.fetchIntersecCoords(verbose, intersection_coordinates)
		elevation_profile = Create.createNumpyArray(verbose, list(shapely_elevation_profile.coords), 'Profile Coordinates')
		sliced_ep_profile = Create.createSlicedElevProfile(verbose, elevation_profile, config.num_of_slices, int1, int2)
		factor_of_safety = Perform.FOS_Method(fos, sliced_ep_profile, shapely_circle, config, FOS)
		
		if factor_of_safety < 1:
			# ep_profile = arraylinspace2d(elevation_profile, config.num_of_slices)
			trimmed = Format.trimCircleCoordinates(shapely_circle, list(data))
			plt.plot(trimmed[:, 0], trimmed[:, 1])
			ep_profile = data
			plt.plot(ep_profile[:, 0], ep_profile[:, 1])


class Perform(object):
	@staticmethod
	def FOS_Method(verbose, method, config, sliced_ep_profile, shapely_circle, fos_trial=1.2):
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
		effective_friction_angle = config.effective_friction_angle_soil; bulk_density = config.bulk_density
		soil_cohesion = config.soil_cohesion; vslice = config.vslice; water_pore_pressure = config.water_pore_pressure
		percentage_status = config.percentage_status
		effective_angle = effective_friction_angle
	
		General.verb(verbose, 'Performing actual FOS calculation by Method: %s' % method)
		# Some checks to see if parameters passed are the right objects and set correctly
		if sliced_ep_profile.ndim != 2:
			General.raiseGeneralError("Numpy array is wrong size, %d, needs to be 2" % sliced_ep_profile.ndim)
		
		if not isinstance(shapely_circle, LineString):
			General.raiseGeneralError("Shapely_circle is somehow not a LineString object")
		
		if not Analysis.isInt(bulk_density):
			General.raiseGeneralError("Bulk Density is somehow not an integer")
		
		if not Analysis.isInt(soil_cohesion):
			General.raiseGeneralError("Soil Cohesion is somehow not an integer")
		
		if not Analysis.isInt(effective_friction_angle):
			General.raiseGeneralError("Effective Friction Angle is somehow not an integer")
		
		if vslice <= 0:
			print '\r\nvslice can not be 0 or less: Setting default: 50.\r\n'
			vslice = 50
		
		if not Analysis.isInt(water_pore_pressure):
			if int(water_pore_pressure) == 0:
				water_pore_pressure = 0
			else:
				General.raiseGeneralError("Water Pore Pressure is not an integer")
		elif water_pore_pressure < 0:
			General.raiseGeneralError("Water Pore Pressure cannot be a negative number: water_pore_pressure= %d" %
			                          water_pore_pressure)
		else:
			General.verb(verbose, "Water Pressure Set at %d" % water_pore_pressure)
		
		if percentage_status == 'on':
			percentage_status = True
		elif percentage_status == 'off':
			percentage_status = False
		else:
			General.raiseGeneralError(
				"Percentage_status is not configured correctly: percentage_status = %s" % percentage_status)
		
		### Perform actual calculation of forces slice-by-slice
		numerator_list = []
		denominator_list = []
		errors = 0
		slice = 1
		for index in range(len(sliced_ep_profile) - 1):
			try:
				### Isolate variables of individual slice ##
				length, degree, mg, prof_length, prof_degree = Format.isolate_slice(index, sliced_ep_profile,
				                                                                    shapely_circle, bulk_density)
				effective_angle = Calc.degree2rad(effective_angle)
				
				# Calculate numerator and denominator of individual slice based on method
				numerator, denominator = Calc.FOS_calc(method,
				                                          water_pore_pressure,
				                                          mg,
				                                          degree,
				                                          effective_angle,
				                                          soil_cohesion,
				                                          length,
				                                          fos_trial)
				
				numerator_list.append(numerator)
				denominator_list.append(denominator)
				
				# Print slices as they are calculated - turned off and on in config file.
				General.printslice(verbose, slice, vslice, percentage_status, sliced_ep_profile)
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
		General.printResults(verbose, error_result, method, soil_cohesion, effective_friction_angle, bulk_density,
		                     slice,
		                     water_pore_pressure,
		                     factor_of_safety)
		return factor_of_safety
	
	@staticmethod
	def perform_critical_slope_sim(verbose, config, data, method, FOS=1.2):
		General.verb(verbose, "Starting Critical Slope Analysis")
		fos = method
		# find boundaries
		x = config.c_x
		y = config.c_y
		a, b = config.c_a, config.c_b
		r = config.c_r
		mult = .25
		
		expand_ab = True
		add_ab = True
		
		while expand_ab:
			try:
				Calc.sim_calc(False, x, y, a, b, r, data, config, fos, FOS)
			except:
				General.verb(verbose, ("Failed on (%s,%s)" % (str(a), str(b))))
				a = config.c_a + 1
				b = config.c_b + 1
				if add_ab is False:
					break
				add_ab = False
			
			if add_ab:
				a += mult
				b += mult
			else:
				a -= mult
				b -= mult
		"""
		while expand_ab:
			sim_calc(False, x, y, a, b, r, data, config, fos)
			a += 1
			b += 1
			"""
		plt.show()
		
		if config.save_figure == 'yes':
			General.verb(verbose, 'Saving result to figure.')
			plt.savefig('slope_profile.tif')


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
				if not Analysis.contains("=", line):
					General.raiseGeneralError("Could not find an '=' %d: %s" % (line_num, line))
				
				variable = line.split()[0]
				equal = line.split()[1]
				value = line.split()[2]
				if len(line.split()) > 3:
					General.raiseGeneralError("Wrong Syntax on line, %s: %s" % (line_num, line))
				if equal != '=':
					sys.exit("This shouldn't appear.Ever.")
				if not variable in str(self.options_from_config):
					General.raiseGeneralError("Couldn't find %s in options_from_config list" % variable)
				else:
					# print variable, equal, value
					if variable == self.options_from_config[0]:
						# delimeter - string
						self.delimit = Analysis.isString(value, variable)
					
					elif variable == self.options_from_config[1]:
						# circle_coordinates
						if not Analysis.hasComma(value):
							General.raiseGeneralError("Wrong Circle Coordinates - Check Config File")
						else:
							if Analysis.isEllipseFormat(value):
								value = Format.formatCircleData(value)
								self.c_x = float(value[0])
								self.c_y = float(value[1])
								self.c_a = float(value[2])
								self.c_b = float(value[3])
							
							else:
								value = Format.formatCircleData(value)
								self.c_x = float(value[0])
								self.c_y = float(value[1])
								self.c_r = float(value[2])
					
					elif variable == self.options_from_config[2]:
						# soil cohesion - float
						self.soil_cohesion = Analysis.isFloat(value)
					
					elif variable == self.options_from_config[3]:
						# internal friction angle - float
						self.effective_friction_angle_soil = Analysis.isFloat(value)
					
					elif variable == self.options_from_config[4]:
						# bulk density - float
						self.bulk_density = Analysis.isFloat(value)
					
					elif variable == self.options_from_config[5]:
						# number of slices - int
						self.num_of_slices = Analysis.isInt(value)
					
					elif variable == self.options_from_config[6]:
						# save figure - string
						self.save_figure = Analysis.isString(value, variable)
					
					elif variable == self.options_from_config[7]:
						# show figure - string
						self.show_figure = Analysis.isString(value, variable)
					
					elif variable == self.options_from_config[8]:
						# water pore pressure - float
						self.water_pore_pressure = Analysis.isFloat(value)
					
					elif variable == self.options_from_config[9]:
						# vslice bulk output - int
						self.vslice = Analysis.isInt(value)
					
					elif variable == self.options_from_config[10]:
						# Display percentage status - string
						self.percentage_status = Analysis.isString(value, variable)
					
					elif variable == self.options_from_config[11]:
						# verbose switch - string
						self.verbose = Analysis.isString(value, variable)
					
					elif variable == self.options_from_config[12]:
						# perform critical slope analysis
						self.perform_critical_slope = Analysis.isString(value, variable)
					else:
						General.raiseGeneralError("Variable not found in options from config file: %s" % variable)
			
			line_num += 1