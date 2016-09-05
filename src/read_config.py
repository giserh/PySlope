import analyze_utils as Analysis
import general_utils as General
import sys
import format_utils as Format

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
		'trial_fos',  # 13
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
				if len(line.split()) > 3: General.raiseGeneralError("Wrong Syntax on line, %s: %s" % (line_num, line))
				if equal != '=': sys.exit("This shouldn't appear.Ever.")
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
					
					elif variable == self.options_from_config[13]:
						# trial fos value
						self.trial_fos = Analysis.isFloat(value)
					else:
						General.raiseGeneralError("Variable not found in options from config file: %s" % variable)
			
			line_num += 1