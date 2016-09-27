class ReadConfig(object):
	def __init__(self, file_name, *args):
		self.options_from_config = []
		self.variable = []
		self.value = []
		self.value_dict = {}
		
		for num in args[0]:
			self.options_from_config.append(num)
			
		self.file_name = file_name
		
		# open file and read contents to store in variables
		with open(file_name) as f:
			content = f.readlines()
		line_num = 1
		for line in content:
			if not line.startswith('#') and not line.isspace():
				if not self.contains("=", line):
					exit("Could not find an '=' %d: %s" % (line_num, line))
				
				
				equal = line.split()[1]
				
				if len(line.split()) > 3:
					exit("Wrong Syntax on line, %s: %s" % (line_num, line))
				if equal != '=':
					exit("Could not find '=' on line %s : %s" % (line_num, line))
				var, val = line.split()[0], line.split()[2]
				self.value_dict[var] = val
				
			line_num += 1
		for val in self.variable:
			if val not in self.options_from_config:
				exit("Could not find '%s' in config file" % val)
		
		self.value_list = self.value
	
	def return_variables(self):
		return self.value_dict
	
	def contains(self, character, string):
		equals = 0
		for char in string:
			if char == character:
				equals += 1
		if equals == 0:
			return False
		else:
			return True