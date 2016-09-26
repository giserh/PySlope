import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import create_utils as Create
import sys
def verb(v, string):
	'''Prints verbose string to terminal'''
	if v:
		print '-> %s' % string

def raiseGeneralError(arg):
	'''Raises standard error'''
	raise StandardError(arg)

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
			print 'Calculating Slice: %s %s' % (str(slice), display_percentage_status(percentage_status,
			                                                                                  sliced_ep_profile.size,
			                                                                                  slice))
	except:
		pass

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
		results = error_result + '\n\nMethod: {}\nCohesion: {} kPa\nEffective Friction Angle: {}\nBulk Density: {} ' \
		                         'Kg/m^3\nNumber of ' \
		                         'slices ' \
		                         'calculated: {}\nWater Pore Pressure: {} kPa\n\nFactor of Safety: {}\n'.format(
			                         method.title(),
			                         soil_cohesion,
			                         effective_friction_angle,
			                         bulk_density,
			                         slice,
			                         water_pore_pressure,
			                         str(factor_of_safety))
	else:
		results = "Factor of Safety: {}".format(str(factor_of_safety))
	
	with open('results.txt', 'w') as f:
		f.write(results)
	print results



def previewGeometery(verbose, config, profile_data):
	if config.show_figure == 'on':
		circle_preview = Create.generateEllipse(verbose, config)
		plt.plot(profile_data[:, 0], profile_data[:, 1], color='red')
		plt.grid(True)
		#plt.axes().set_aspect('equal', 'datalim')
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

def display_percentage_status(percentage_status, size, slice):
	"""Returns String of Percentage Status"""
	if percentage_status:
		num_elements = float(size / 2)
		perc = (slice / num_elements) * 100
		
		return " | (%d%%)" % perc
	else:
		return ''


class Index(object):
	def abort_gui(self, event):
		sys.exit("Exitting")
	
	def cont_gui(self, event):
		print '-> Proceeding'
		plt.close('all')