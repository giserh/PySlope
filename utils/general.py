import create
import format
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

class Index(object):
	def abort_gui(self, event):
		exit("Aborting.")
	def cont_gui(self, event):
		verb(True, "Proceeding")
		plt.close('all')
		
def previewGeometry(config):
	circle = create.ellipse(config)
	profile = format.load_profile_data(config)
	plt.plot(profile[:, 0], profile[:,1], color='red')
	plt.grid(True)
	plt.xlabel("Spatial Distance - X")
	plt.ylabel("Height of Profile - Y")
	plt.scatter(circle[:, 0], circle[:, 1])
	buttonopt = Index()
	quitax = plt.axes([0.7, 0.05, 0.1, 0.075])
	contax = plt.axes([0.81, 0.05, 0.1, 0.075])
	quit = Button(quitax, 'Quit')
	quit.on_clicked(buttonopt.abort_gui)
	cont = Button(contax, 'Continue')
	cont.on_clicked(buttonopt.cont_gui)
	plt.show()
	plt.close()

def verb(verbose, string):
	if not verbose: return
	print '--> {}'.format(string)
	return

def printslice(config, slice, sprofile):
	if slice % int(config.vslice) == 0:
		verb(config.verbose, "Calculating slice: {} {}"
		                     "".format(slice,
		                               display_percentage_status(config,
		                                                         sprofile.size,
		                                                         slice)))

def display_percentage_status(config, size, slice):
	if not config.percentage_status: return ''
	num_elements = float(size / 2)
	perc = (int(slice) / num_elements) * 100
	
	return " | ({}%)".format(perc)
		