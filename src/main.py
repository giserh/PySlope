#!/usr/bin/env python

import numpy as np
from shapely.geometry import LineString, Point, Polygon
import sys, math, itertools
import scipy as sp
import matplotlib.pyplot as plt
from utils import *
from fos import *

### Initialize Variables ###
delimit = ''
soil_cohesion = -1
bulk_density = -1
num_of_elements = -1
effective_friction_angle_soil = -1
show_figure = ''
save_figure = ''
circle_data = ''
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
        """ Add to list to search for options that
        should be in the config file
        """

        'delimit',
        'circle_data'
        'soil_cohesion',
        'effective_friction_angle_soil',
        'bulk_density',
        'num_of_elements',
        'show_figure',
        'save_figure',
        'water_pore_pressure',
        'vslice',
        'percentage_status',
        'FOS',
        'verbose'
    ]


class ReadConfig(object):

    def __init__(self, file_name):
        ## General ##
        global delimiter, soil_cohesion, bulk_density, num_of_elements, show_figure, save_figure

        ## circle Data ##
        global c_x, c_y, c_r, c_a, c_b

        self.file_name = file_name

        # open file and read contents to store in variables
        with open(file_name) as f:
            content = f.readlines()
        line_num = 1
        for line in content:
            if not line.startswith('#') and not line.isspace():
                if not contains("=", line):
                    sys.exit("Could not find an '=' %d: %s" %  (line_num, line))


                variable = line.split()[0]
                equal    = line.split()[1]
                value    = line.split()[2]
                if len(line.split()) > 3:
                    raiseGeneralError("Wrong Syntax on line, %s: %s" % (line_num, line))
                if equal != '=':
                    sys.exit("This shouldn't appear.Ever.")
                if not variable in str(options_from_config):
                    raiseGeneralError("Couldn't find %s in options_from_config list" % variable)
                else:
                    if isInt(value):
                        globals()[variable] = int(value)
                    elif isFloat(value):
                        globals()[variable] = float(value)
                    elif hasComma(value):
                        ## value has comma in expression
                        if isEllipse(value):
                            value = formatCircleData(value)
                            c_x = float(value[0])
                            c_y = float(value[1])
                            c_a = float(value[2])
                            c_b = float(value[3])
                        else:
                            value = formatCircleData(value)
                            c_x = float(value[0])
                            c_y = float(value[1])
                            c_r = float(value[2])

                    elif isString(value):
                        globals()[variable] = str(value)


            line_num += 1

def fos(fos, config_file, data_file):


    #### set variables from the configuration file
    global \
        verbose, delimit, soil_cohesion, bulk_density, \
        num_of_elements, show_figure, save_figure, water_pore_pressure, vslice, \
        percentage_status


    ReadConfig(config_file)

    verbose = True if verbose == 'yes' else False
    effective_angle, angle = effective_friction_angle_soil, effective_friction_angle_soil
    ####
    #
    #
    #### load data from file as numpy array
    verb(verbose, 'Load data from file as numpy array.')

    data = np.loadtxt(data_file, delimiter=delimit)
    ####
    #
    #### Check to see if num_of_elements is lower than actual length of data:
    verb(verbose, 'Check to see if num_of_elements is lower than actual length of data.')
    if num_of_elements < len(data):
        print "Error: You can't have num_of_elements set lower to your total amount of data points" \
              "\n\nTotal Data Points: %s" \
              "\nNum_of_elements: %s" % (str(len(data)), str(int(num_of_elements)))
        sys.exit()
    #
    ## create shapely circle with circle data
    verb(verbose, 'Creating Shapely circle with circle data.')
    #shapely_circle = Point(c_x, c_y).buffer(c_r).boundary

    try:
        verb(verbose, 'Trying to generate ellipse')
        if c_x is not None or c_y is not None or c_b is not None or c_a is not None:
            ellipse = generateEllipse(c_x, c_y, c_a, c_b)
            shapely_circle = LineString(ellipse)
        else:
            sys.exit("Error: c_x, c_y, c_a, c_b not set.. Report bug")
    except:
        verb(verbose, 'Ellipse failed: Reverting to perfect circle.')
        if c_x is not None or c_y is not None or c_r is not None:
            shapely_circle = Point(c_x, c_y).buffer(c_r).boundary
        else:
            sys.exit("Error: c_x, c_y, c_r not set.. Report bug")
    #
    #
    ## create shapely line with elevation profile
    verb(verbose, 'Creating Shapely line with elevation profile.')
    shapely_elevation_profile = LineString(data)
    intersection_coordinates = list(shapely_circle.intersection(shapely_elevation_profile).bounds)
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
    ep_profile = arraylinspace2d(elevation_profile, num_of_elements)
    sliced_ep_profile = slice_array(ep_profile, int1, int2, num_of_elements)
    #
    #
    #
    ### Perform actual calculation of forces slice-by-slice
    verb(verbose, 'Performing actual FOS calculation by Method: %s' % fos)
    effective_friction_angle = effective_angle

    results = ''
    if fos == 'general':
        results = FOS_Method_Slices(sliced_ep_profile,
                                    shapely_circle,
                                    bulk_density,
                                    soil_cohesion,
                                    effective_friction_angle,
                                    vslice,
                                    percentage_status
                                    )

    elif fos == 'bishop':
        print 'performing bishop method'

    else:
        raiseGeneralError("Method: %s didn't execute" % fos)

    print results

    plt.scatter(circle_coordinates[:,0], circle_coordinates[:,1], color='red')
    plt.scatter(ep_profile[:,0], ep_profile[:,1])
    plt.scatter(sliced_ep_profile[:,0], sliced_ep_profile[:,1], color='green')


    if save_figure == 'yes':
        verb(verbose, 'Saving result to figure.')
        plt.savefig('slope_profile.tif')

    if show_figure == 'yes':
        verb(verbose, 'Show figure: True.')
        plt.show()

