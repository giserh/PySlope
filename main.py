from utils.configreader import ReadConfig
from utils.db import DB
from utils.general import previewGeometry
from utils import create
from utils import format
from utils import perform
import matplotlib.pyplot as plt
NUM_OF_VARS = 17

def data_manipulation(variables):
	variables['ellipse_coordinates'] = map(float, variables['ellipse_coordinates'].split(','))
	variables['verbose'] = True if variables['verbose'] == 'yes' else False
	variables['save_figure'] = True if variables['save_figure'] == 'yes' else False
	variables['show_figure'] = True if variables['show_figure'] == 'yes' else False
	variables['save_figure'] = True if variables['save_figure'] == 'yes' else False
	variables['percentage_status'] = True if variables['percentage_status'] == 'yes' else False
	variables['perform_critical_slope'] = True if variables['perform_critical_slope'] == 'yes' else False
	
	return variables

def main(*args):
	if NUM_OF_VARS != len(args): exit("\nLength of variables does not match arguments passed to main()")

	method = args[0]
	fos_trial = args[1]
	soil_cohesion = args[2]
	inter_fric = args[3]
	numslices = args[4]
	water_pres = args[5]
	vslice = args[6]
	percent = args[7]
	verbose = args[8]
	save = args[9]
	show = args[10]
	do_crit_slope = args[11]
	ellip_coor = args[12]
	delimiter = args[13]
	bulk = args[14]
	f_config = args[15]
	f_data = args[16]
	

	variables = {
		'method' : method,
		'fos_trial' : fos_trial,
		'soil_cohesion' : soil_cohesion,
		'internal_friction_angle' : inter_fric,
		'num_of_slices' : numslices,
		'water_pressure' :  water_pres,
		'vslice' : vslice,
		'percentage_status' : percent,
		'verbose' : verbose,
		'save_figure' : save,
		'show_figure' : show,
		'perform_critical_slope' : do_crit_slope,
		'ellipse_coordinates' : ellip_coor,
		'delimiter' : delimiter,
		'bulk_density' : bulk,
		'f_config' : f_config,
		'f_data' : f_data
	}
	# read values from config files
	config_values = ReadConfig(f_config, variables.keys()).return_variables()
	
	# sort through None types and replace with value from config file
	for var in variables.keys():
		if variables[var] is not None: continue
		for opt in config_values.keys():
			if var == opt:
				variables[var] = config_values[opt]
		
	# create variable storage object
	config = DB(data_manipulation(variables))
	
	# preview geometry
	if config.show_figure: previewGeometry(config)
	
	# create working space
	sprofile, circle, circ_coords = create.working_space(config, format.load_profile_data(config))
	
	# perform slope stability calculation
	fos, errstr = perform.calculation(config, sprofile, circle)
	
	# plot final diagram
	if config.show_figure:
		profile = format.linspace2d(format.load_profile_data(config), config.num_of_slices)
		plt.scatter(circ_coords[:,0], circ_coords[:,1], color="red")
		plt.plot(sprofile[:,0], sprofile[:,1], color="green")
		plt.plot (profile[:,0], profile[:,1], color="green")
		if config.save_figure:
			plt.savefig('slope_profile.tif')
		plt.show()
	
	print fos, errstr
	#display.results(config, results)
		