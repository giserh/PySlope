
class DB(object):
	
	def __init__(self, variables):
		for key in variables:
			setattr(self, key, variables[key])
	
	def get_attrs(self):
		return self.__dict__