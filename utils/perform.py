import numpy as np
from shapely.geometry import LineString, Point
import general
import calc


def calculation(config, sprofile, circle):
	def _errmsg(obj_name, obj_type, Type):
		try:
			config.__dict__[obj_name] = Type(config.__dict__[obj_name])
		except:
			exit("{} can't be {}".format(obj_name, obj_type))
	
		
	general.verb(config.verbose, "Beginning Calculation of method: {}".format(config.method))
	if sprofile.ndim != 2: exit("Numpy array is wrong size, {}, needs to be 2."
	                            "".format(sprofile.ndim))
	if not isinstance(config.water_pressure, float) : _errmsg("water_pressure", type(config.water_pressure), float)
	if not isinstance(config.soil_cohesion, float)  : _errmsg("soil_cohesion", type(config.soil_cohesion), float)
	if not isinstance(config.internal_friction_angle, float): _errmsg("internal_friction_angle", type(config.internal_friction_angle), float)
	if not isinstance(config.num_of_slices, int)    : _errmsg("num_of_slices", type(config.num_of_slices), int)
	if not isinstance(config.bulk_density, float)   : _errmsg("bulk_density", type(config.bulk_density), float)
	if not isinstance(config.method, str)   : _errmsg("method", type(config.method), str)
	if not isinstance(config.vslice, int)   : _errmsg("vslice", type(config.vslice), int)
	if not isinstance(config.fos_trial, float): _errmsg("fos_trial", type(config.fos_trial), float)
	if not isinstance(circle, LineString)   : _errmsg("circle", type(circle), LineString)
	
	if config.method.lower() == 'general':
		return do_general(config, sprofile, circle)
	
	elif config.method.lower() == 'bishop':
		return do_bishop(config, sprofile, circle)
	else:
		raise StandardError("Method isn't recognized.")
	


def do_general(config, sprofile, circle):
	num_lst, denom_list = [], []
	errs, slice = 0, 1
	for index in range(len(sprofile) - 1):
		try:
			lngth, deg, mg, prof_length, prof_degree = calc.isolate_slice(index, config, sprofile, circle)
			package = {
				'length': lngth,
				'degree': deg,
				'mg': mg,
			}
			
			mg = package['mg']
			l = package['length']
			deg = package['degree']
			eff = np.deg2rad(config.internal_friction_angle)
			c = config.soil_cohesion
			denom = mg * np.sin(deg)
			
			if config.water_pressure == 0:
				num = (mg * np.cos(deg)) * np.tan(eff) + (c * l)
			
			elif config.water_pressure > 0:
				num = c * l + (mg * np.cos(deg) - config.water_pressure * l) * np.tan(eff)
			
			general.printslice(config, slice, sprofile)
			slice += 1
			num_lst.append(num), denom_list.append(denom)
		
		except:
			errs += 1
	numerator_list, denominator_list = np.array(num_lst), np.array(denom_list)
	success = 100 - (float(errs) / float(slice))
	err_result = "\nTotal number of errors encountered: %s\nPercent Success: %f%%" % (str(errs), (success))
	fos = numerator_list.sum() / denominator_list.sum()
	return fos, err_result
	

def do_bishop(config, sprofile, circle):
	def _tol(a, b, tol):
		return True if abs(a - b) < tol else False
	
	step = 0.01
	tol = 0.01
	FOS = config.fos_trial
	while 1:
		num_lst, denom_list = [], []
		errs, slice = 0, 1
		for index in range(len(sprofile) - 1):
			try:
				lngth, deg, mg, prof_length, prof_degree = calc.isolate_slice(index, config, sprofile, circle)
				package = {
					'length': lngth,
					'degree': deg,
					'mg': mg,
				}
				
				mg = package['mg']
				l = package['length']
				deg = package['degree']
				eff = np.deg2rad(config.internal_friction_angle)
				c = config.soil_cohesion
				denom = mg * np.sin(deg)
				
				if config.water_pressure == 0:
					num = (c * l + (mg * np.cos(deg)) *
					             np.tan(eff))
					num = (num / np.cos(deg) + (np.sin(deg) * np.tan(eff) / FOS))
				
				elif config.water_pressure > 0:
					numerator = (
					c * l + (mg * np.cos(deg) - config.water_pressure * l * np.cos(deg)) *
					np.tan(eff))
					num = (numerator / np.cos(deg) + (np.sin(deg) * np.tan(eff) / config.fos_trial))
				
				slice += 1
				num_lst.append(num), denom_list.append(denom)
			
			except:
				errs += 1
		numerator_list, denominator_list = np.array(num_lst), np.array(denom_list)
		fos = numerator_list.sum() / denominator_list.sum()
		print "fos:{} | trial:{}".format(fos, FOS)
		
		if _tol(FOS, fos, tol):
			return fos, None
		
		if fos < config.fos_trial:
			FOS -= step
		elif fos > config.fos_trial:
			FOS += step