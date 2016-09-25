import general_utils as General
import analyze_utils as Analysis
import format_utils as Format
import calc_utils as Calc
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString

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
	effective_friction_angle = config.effective_friction_angle_soil;
	bulk_density = config.bulk_density
	soil_cohesion = config.soil_cohesion;
	vslice = config.vslice;
	water_pore_pressure = config.water_pore_pressure
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
	
	if method == 'bishop':
		step = 0.001
		tol = 0.001
		def _tol(a, b, tol):
			return True if abs(a - b) < tol else False
		
		error_result, factor_of_safety = None, None
		while 1:
			factor_of_safety, error_result = Calc.perform_slicebyslice(False, sliced_ep_profile, shapely_circle, bulk_density,
		                          effective_angle, method, water_pore_pressure, soil_cohesion,
		                          fos_trial, vslice, percentage_status)
			if _tol(fos_trial, factor_of_safety, tol):
				break
			
			if factor_of_safety < fos_trial:
				fos_trial -= step
			elif factor_of_safety > fos_trial:
				fos_trial += step
				
		# Finish up with so
		General.printResults(False, error_result, method, soil_cohesion, effective_friction_angle,
		                     bulk_density,
		                     slice,
		                     water_pore_pressure,
		                     factor_of_safety)
		return factor_of_safety

	else:
		factor_of_safety, error_result = Calc.perform_slicebyslice(verbose, sliced_ep_profile, shapely_circle, bulk_density,
		                                   effective_angle, method, water_pore_pressure, soil_cohesion,
		                                   fos_trial, vslice, percentage_status)
		
		
		# Finish up with so
		General.printResults(verbose, error_result, method, soil_cohesion, effective_friction_angle, bulk_density,
		                     slice,
		                     water_pore_pressure,
		                     factor_of_safety)
		return factor_of_safety



def perform_critical_slope_sim(verbose, config, data, method, fos_trial=1.2):
	General.verb(verbose, "Starting Critical Slope Analysis")
	# find boundaries
	a, b = config.c_a, config.c_b
	mult = .25
	
	expand_ab = True
	add_ab = True
	
	while expand_ab:
		try:
			Calc.sim_calc(verbose, data, config, method, fos_trial)
		except:
			General.verb(verbose, ("Failed on (%s,%s)" % (str(a), str(b))))
			config.c_a = a + 1
			config.c_b = b + 1
			if add_ab is False:
				break
			add_ab = False
		
		if add_ab:
			config.c_a += mult
			config.c_b += mult
		else:
			config.c_a -= mult
			config.c_b -= mult
	"""
	while expand_ab:
		sim_calc(False, x, y, a, b, r, data, config, fos)
		a += 1
		b += 1
		"""
	plt.show()
	
	if config.save_figure == 'on':
		General.verb(verbose, 'Saving result to figure.')
		plt.savefig('slope_profile.tif')