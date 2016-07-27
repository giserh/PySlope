#!/usr/bin/env python

import numpy as np
from shapely.geometry import LineString, Point, Polygon
import sys, math, itertools
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from utils import *
from fos import *

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
    # Circle Data #
    c_x = 0.
    c_y = 0.
    # perfect circle #
    c_r = 0.
    # Ellipse #
    c_a = 0.
    c_b = 0.
    
    options_from_config = [
            'delimiter',                        # 0
            'circle_coordinates',               # 1
            'soil_cohesion',                    # 2
            'effective_friction_angle_soil',    # 3
            'bulk_density',                     # 4
            'num_of_slices',                    # 5
            'show_figure',                      # 6
            'save_figure',                      # 7
            'water_pore_pressure',              # 8
            'vslice',                           # 9
            'percentage_status',                # 10
            'verbose',                          # 11
        ]

    def __init__(self, file_name):

        self.file_name = file_name

        # open file and read contents to store in variables
        with open(file_name) as f:
            content = f.readlines()
        line_num = 1
        for line in content:
            if not line.startswith('#') and not line.isspace():
                if not contains("=", line):
                    raiseGeneralError("Could not find an '=' %d: %s" %  (line_num, line))


                variable = line.split()[0]
                equal    = line.split()[1]
                value    = line.split()[2]
                if len(line.split()) > 3:
                    raiseGeneralError("Wrong Syntax on line, %s: %s" % (line_num, line))
                if equal != '=':
                    sys.exit("This shouldn't appear.Ever.")
                if not variable in str(self.options_from_config):
                    raiseGeneralError("Couldn't find %s in options_from_config list" % variable)
                else:
                    #print variable, equal, value

                    if variable == self.options_from_config[0]:
                        #delimeter - string
                        self.delimit = isString(value, variable)

                    elif variable == self.options_from_config[1]:
                        # circle_coordinates
                        if not hasComma(value):
                            raiseGeneralError("Wrong Circle Coordinates - Check Config File")
                        else:
                            if isEllipse(value):
                                value = formatCircleData(value)
                                self.c_x = float(value[0])
                                self.c_y = float(value[1])
                                self.c_a = float(value[2])
                                self.c_b = float(value[3])

                            else:
                                value = formatCircleData(value)
                                self.c_x = float(value[0])
                                self.c_y = float(value[1])
                                self.c_r = float(value[2])

                    elif variable == self.options_from_config[2]:
                        # soil cohesion - float
                        self.soil_cohesion = isFloat(value,variable)

                    elif variable == self.options_from_config[3]:
                        # internal friction angle - float
                        self.effective_friction_angle_soil = isFloat(value, variable)

                    elif variable == self.options_from_config[4]:
                        # bulk density - float
                        self.bulk_density = isFloat(value, variable)

                    elif variable == self.options_from_config[5]:
                        # number of slices - int
                        self.num_of_slices = isInt(value, variable)

                    elif variable == self.options_from_config[6]:
                        # save figure - string
                        self.save_figure = isString(value, variable)

                    elif variable == self.options_from_config[7]:
                        # show figure - string
                        self.show_figure = isString(value, variable)

                    elif variable == self.options_from_config[8]:
                        # water pore pressure - float
                        self.water_pore_pressure = isFloat(value, variable)

                    elif variable == self.options_from_config[9]:
                        # vslice bulk output - int
                        self.vslice = isInt(value, variable)

                    elif variable == self.options_from_config[10]:
                        # Display percentage status - string
                        self.percentage_status = isString(value, variable)

                    elif variable == self.options_from_config[11]:
                        # verbose switch - string
                        self.verbose = isString(value, variable)
                    else:
                        raiseGeneralError("Variable not found in options from config file: %s" % variable)

            line_num += 1

def fos(fos, config_file, data_file):

    config = ReadConfig(config_file)

    verbose = True if config.verbose == 'yes' else False
    effective_angle, angle = config.effective_friction_angle_soil, config.effective_friction_angle_soil
    ####
    #
    #
    #### load data from file as numpy array
    verb(verbose, 'Load data from file as numpy array.')

    data = np.loadtxt(data_file, delimiter=config.delimit)
    ####
    #
    #### Check to see if num_of_elements is lower than actual length of data:
    verb(verbose, 'Check to see if num_of_elements is lower than actual length of data.')
    if config.num_of_slices < len(data):
        print "Error: You can't have num_of_elements set lower to your total amount of data points" \
              "\n\nTotal Data Points: %s" \
              "\nNum_of_elements: %s" % (str(len(data)), str(int(config.num_of_slices)))
        sys.exit()
    #
    ## create shapely circle with circle data
    verb(verbose, 'Creating Shapely circle with circle data.')
    #shapely_circle = Point(c_x, c_y).buffer(c_r).boundary

    try:
        verb(verbose, 'Trying to generate ellipsoid')
        if config.c_x is not None or config.c_y is not None or config.c_b is not None or config.c_a is not None:
            ellipse = generateEllipse(config.c_x, config.c_y, config.c_a, config.c_b)
            shapely_circle = LineString(ellipse)
        else:
            sys.exit("Error: c_x, c_y, c_a, c_b not set.. Report bug")
    except:
        verb(verbose, 'Ellipse failed: Reverting to perfect circle.')
        if config.c_x is not None or config.c_y is not None or config.c_r is not None:
            shapely_circle = Point(config.c_x, config.c_y).buffer(config.c_r).boundary
        else:
            sys.exit("Error: c_x, c_y, c_r not set.. Report bug")
    #
    #
    ## create shapely line with elevation profile
    verb(verbose, 'Creating Shapely line with elevation profile.')
    shapely_elevation_profile = LineString(data)
    intersection_coordinates = list(shapely_circle.intersection(shapely_elevation_profile).bounds)

    #### Preview geometery ####
    circle_preview = np.array(list(shapely_circle.coords))
    plt.plot(data[:,0], data[:,1], color='red')
    plt.scatter(circle_preview[:,0], circle_preview[:,1])

    buttonopt = Index()
    quitax = plt.axes([0.7, 0.05, 0.1, 0.075])
    contax = plt.axes([0.81, 0.05, 0.1, 0.075])
    quit = Button(quitax, 'Quit')
    quit.on_clicked(buttonopt.abort_gui)
    cont = Button(contax, 'Continue')
    cont.on_clicked(buttonopt.cont_gui)
    plt.show()
    #
    if len(intersection_coordinates) == 0:
        print "Error: Circle doesn't intersect the profile - please readjust circle coordinates in config file"
        sys.exit()
    #
    ## Using intersection coordinates isolate the section of profile that is within the circle.
    ### Check to see if intersection_coordinates length is 4 elements.. if it isn't so that means for some reason
    # there are moreless than two intersection points in the profile - shouldn't really happen at all...
    if len(intersection_coordinates) != 4:
        print "Error: Found more/less than two intersection coordinates\nNumber of intersections: %s" % \
              str(len(intersection_coordinates))
        sys.exit()
    verb(verbose, 'Isolating section of profile: Length of element is correct.')
    int1, int2 = (intersection_coordinates[0], intersection_coordinates[1]), (intersection_coordinates[2],
                                                                              intersection_coordinates[3])
    #
    # Check to see if intersection_1 and intersection_2 are the same. If they are that means the circle only intersects
    # the profile once.. not allowed
    if int1 == int2:
        print "Error: Circle only intersects the profile in one place - please readjust circle coordinates in config file"
        sys.exit()
    verb(verbose, 'Cross-checking intersection coordinates.')

    verb(verbose, 'Converting circle/ellipse coordinates into Numpy Array.')
    circle_coordinates = np.array(list(shapely_circle.coords))
    verb(verbose, 'Converting profile coordinates into Numpy Array.')
    elevation_profile = np.array(list(shapely_elevation_profile.coords))

    #plt.scatter(circle_coordinates[:,0], circle_coordinates[:,1], color='red')
    #plt.scatter(elevation_profile[:,0], elevation_profile[:,1])
    #plt.show()
    #
    #
    # Create sliced array with boundaries from ep_profile
    verb(verbose, 'Creating Numpy array of sliced profile bounded within circle.')
    ep_profile = arraylinspace2d(elevation_profile, config.num_of_slices)
    sliced_ep_profile = slice_array(ep_profile, int1, int2, config.num_of_slices)
    #
    #
    #
    ### Perform actual calculation of forces slice-by-slice
    verb(verbose, 'Performing actual FOS calculation by Method: %s' % fos)
    effective_friction_angle = effective_angle

    results = ''
    if fos == 'general':
        results = FOS_Method( fos,
                                     sliced_ep_profile,
                                     shapely_circle,
                                     config.bulk_density,
                                     config.soil_cohesion,
                                     effective_friction_angle,
                                     config.vslice,
                                     config.percentage_status,
                                     config.water_pore_pressure,
                                     verbose)

    elif fos == 'bishop':
        results = FOS_Method(fos,
                             sliced_ep_profile,
                             shapely_circle,
                             config.bulk_density,
                             config.soil_cohesion,
                             effective_friction_angle,
                             config.vslice,
                             config.percentage_status,
                             config.water_pore_pressure,
                             verbose)

    else:
        raiseGeneralError("Method: %s didn't execute" % fos)

    print results

    plt.scatter(circle_coordinates[:,0], circle_coordinates[:,1], color='red')
    plt.scatter(ep_profile[:,0], ep_profile[:,1])
    plt.scatter(sliced_ep_profile[:,0], sliced_ep_profile[:,1], color='green')


    if config.save_figure == 'yes':
        verb(verbose, 'Saving result to figure.')
        plt.savefig('slope_profile.tif')

    if config.show_figure == 'yes':
        verb(verbose, 'Show figure: True.')
        plt.show()


