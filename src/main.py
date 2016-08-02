#!/usr/bin/env python

import numpy as np
from shapely.geometry import LineString, Point, Polygon
import sys, math, itertools
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from utils import *
from fos import *


def fos(fos, config_file, data_file):
    if fos is None:
        raiseGeneralError("No method chosen: fos --help")
    config = ReadConfig(config_file)

    verbose = True if config.verbose == 'yes' else False
    ####
    #
    #
    #### load data from file as numpy array
    verb(verbose, 'Load data from file as numpy array.')
    data = np.loadtxt(data_file, delimiter=config.delimit)
    ####
    #
    #### Check to see if num_of_elements is lower than actual length of data:
    verb(verbose, 'Check to see if number of slices is lower than actual length of data.')
    if config.num_of_slices < len(data):
        print "Error: You can't have num_of_elements set lower to your total amount of data points" \
              "\n\nTotal Data Points: %s" \
              "\nNum_of_slices: %s" % (str(len(data)), str(int(config.num_of_slices)))
        sys.exit()
    #

    ## create shapely circle with circle data
    shapely_circle = createShapelyCircle(verbose,
                                         config.c_x,
                                         config.c_y,
                                         config.c_a,
                                         config.c_b,
                                         config.c_r)
    #
    #
    ## find intersection coordinates of shapely_circle and profile data
    intersection_coordinates = intersec_circle_and_profile(verbose, shapely_circle, data)

    # created normal shapley object from raw profile data
    shapely_elevation_profile = LineString(data)

    #### Preview geometery ####
    previewGeometery(config.show_figure, shapely_circle, data)


    #
    ## Using intersection coordinates isolate the section of profile that is within the circle.
    ### Check to see if intersection_coordinates length is 4 elements.. if it isn't so that means for some reason
    # there are more or less than two intersection points in the profile - shouldn't really happen at all...

    int1, int2 = fetchIntersecCoords(verbose, intersection_coordinates)



    circle_coordinates = createNumpyArray(verbose,list(shapely_circle.coords), "Circle/Ellipse")
    elevation_profile = createNumpyArray(verbose, list(shapely_elevation_profile.coords),'Profile Coordinates')
    #
    #
    # Create sliced array with boundaries from ep_profile
    sliced_ep_profile = createSlicedElevProfile(verbose,
                                                elevation_profile,
                                                config.num_of_slices,
                                                int1,
                                                int2)
    #
    #
    #
    ### Perform actual calculation of forces slice-by-slice

    verb(verbose, 'Performing actual FOS calculation by Method: %s' % fos)

    results = ''
    if fos == 'general':
        results = FOS_Method( fos,
                                     sliced_ep_profile,
                                     shapely_circle,
                                     config.bulk_density,
                                     config.soil_cohesion,
                                     config.effective_friction_angle_soil,
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
                             config.effective_friction_angle_soil,
                             config.vslice,
                             config.percentage_status,
                             config.water_pore_pressure,
                             verbose)

    else:
        raiseGeneralError("Method: %s didn't execute" % fos)

    print results

    plt.scatter(circle_coordinates[:,0], circle_coordinates[:,1], color='red')
    ep_profile = arraylinspace2d(elevation_profile, config.num_of_slices)
    plt.scatter(ep_profile[:,0], ep_profile[:,1])
    plt.scatter(sliced_ep_profile[:,0], sliced_ep_profile[:,1], color='green')


    if config.save_figure == 'yes':
        verb(verbose, 'Saving result to figure.')
        plt.savefig('slope_profile.tif')
    """

        verb(verbose, 'Show figure: True.')
        plt.show()
        """


