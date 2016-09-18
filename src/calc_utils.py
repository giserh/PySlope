import numpy as np
import general_utils as General
import matplotlib.pyplot as plt
import create_utils as Create
import format_utils as Format
import perform_utils as Perform

def rad2degree(rad):
	'''Converts radian to degree'''
	return rad * 180. / np.pi


def degree2rad(degree):
	'''Converts degree to radian'''
	return degree * np.pi / 180.



def perform_slicebyslice(verbose, sliced_ep_profile, shapely_circle, bulk_density,
                         effective_angle, method, water_pore_pressure, soil_cohesion,
                         fos_trial, vslice, percentage_status):
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
			effective_angle = degree2rad(effective_angle)
			
			# Calculate numerator and denominator of individual slice based on method
			numerator, denominator = FOS_calc(method,
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
	print factor_of_safety, fos_trial
	return factor_of_safety
	
def iterate(fos_trial, step=0.001, tol=0.001):
	def _tol(a, b, tol):
		return True if abs(a - b) < tol else False
	
	while 1:
		result = func(fos_trial)
		if _tol(fos_trial, result, tol):
			print fos_trial, result
			return (fos_trial + result) /2.
		
		if result < fos_trial:
			fos_trial -= step
		elif result > fos_trial:
			fos_trial += step
			
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


def sim_calc(verbose, data, config, fos, fos_trial=1.2):
	shapely_circle = Create.createShapelyCircle(False, config)
	intersection_coordinates = Format.intersec_circle_and_profile(False, shapely_circle, data)
	shapely_elevation_profile = Create.createShapelyLine(verbose, data)
	int1, int2 = Format.fetchIntersecCoords(verbose, intersection_coordinates)
	elevation_profile = Create.createNumpyArray(verbose, list(shapely_elevation_profile.coords), 'Profile Coordinates')
	sliced_ep_profile = Create.createSlicedElevProfile(verbose, elevation_profile, config, int1, int2)
	factor_of_safety = Perform.FOS_Method(verbose, fos, config, sliced_ep_profile, shapely_circle, fos_trial)
	
	if factor_of_safety < 1:
		# ep_profile = arraylinspace2d(elevation_profile, config.num_of_slices)
		trimmed = Format.trimCircleCoordinates(shapely_circle, list(data))
		plt.plot(trimmed[:, 0], trimmed[:, 1])
		ep_profile = data
		plt.plot(ep_profile[:, 0], ep_profile[:, 1])