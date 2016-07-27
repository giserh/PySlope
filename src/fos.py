import sys
import numpy as np
from utils import *
from shapely.geometry import LineString, Point, Polygon



#### Different FOS Methods ####
def FOS_Method( method,
                sliced_ep_profile,
                 shapely_circle,
                 bulk_density,
                 soil_cohesion,
                 effective_friction_angle,
                 vslice,
                 percentage_status,
                 water_pore_pressure,
                 verbose):
    """
    :param method: a string stating the method of FOS calculation to be used
    :param sliced_ep_profile: a numpy array of the profile that is in the circle of interest
    :param shapely_circle:  a shapely object linestring that has the coorindates of the circle/ellipse
    :param bulk_density:    an integer for bulk_density of the soil
    :param soil_cohesion:   an integer for soil_cohesion of the soil
    :param effective_friction_angle: an integer in degrees of the effective angle of friction
    :param vslice: an integer that determines the modulo per batch of slices that should be outputed to the terminal
    :param percentage_status: a boolian expression to show percentage_status when completing stacks of slices
    :param water_pore_pressure: a positive integer expressing the water_pore_pore in kPa
    :param verbose: boolian expression if verbose statements should be printed to terminal

    :return:
        returns a single float number of the calculated factor of safety from the given parameters
    """
    effective_angle = effective_friction_angle

    ### Some checks to see if parameters passed are the right objects and set correctly ###
    if sliced_ep_profile.ndim != 2:
        raiseGeneralError("Numpy array is wrong size, %d, needs to be 2" % sliced_ep_profile.ndim)

    if not isinstance(shapely_circle, LineString):
        raiseGeneralError("Shapely_circle is somehow not a LineString object")

    if not isInt(bulk_density, 'bulk_density'):
        raiseGeneralError("Bulk Density is somehow not an integer")

    if not isInt(soil_cohesion, 'soil_cohesion'):
        raiseGeneralError("Soil Cohesion is somehow not an integer")

    if not isInt(effective_friction_angle, 'effective_friction_angle'):
        raiseGeneralError("Effective Friction Angle is somehow not an integer")

    if vslice <= 0:
        print '\r\nvslice can not be 0 or less: Setting default: 50.\r\n'
        vslice = 50

    if not isInt(water_pore_pressure, 'water_pore_pressure'):
        if int(water_pore_pressure) == 0:
            water_pore_pressure = 0
        else:
            raiseGeneralError("Water Pore Pressure is not an integer")
    elif water_pore_pressure < 0:
        raiseGeneralError("Water Pore Pressure cannot be a negative number: water_pore_pressure= %d" %
                          water_pore_pressure)
    else:
        verb(verbose, "Water Pressure Set at %d" % water_pore_pressure)

    if percentage_status == 'on':
        percentage_status = True
    elif percentage_status == 'off':
        percentage_status = False
    else:
        raiseGeneralError("Percentage_status is not configured correctly: percentage_status = %s" % percentage_status)

    ### Perform actual calculation of forces slice-by-slice
    numerator_list = []
    denominator_list = []
    errors = 0
    slice = 1
    for index in range(len(sliced_ep_profile)-1):
        try:
            ### Isolate variables of individual slice ##
            length, degree, mg, cohesion = isolate_slice(index, sliced_ep_profile, shapely_circle, bulk_density,
                                                         soil_cohesion)
            effective_angle = degree2rad(effective_angle)

            # Calculate numerator and denominator of individual slice based on method
            numerator, denominator = FOS_calc(method,
                                              water_pore_pressure,
                                              mg,
                                              degree,
                                              effective_angle,
                                              cohesion,
                                              length)

            numerator_list.append(numerator)
            denominator_list.append(denominator)

            # Print slices as they are calculated - turned off and on in config file.
            printslice(slice, vslice, percentage_status, sliced_ep_profile)
            slice += 1

            # Add results to lists that will be used to calculate the FOS in bulk
            numerator_list.append(numerator)
            denominator_list.append(denominator)
        except:
            errors +=1

    # convert calculated lists into numpy arrays
    numerator_list, denominator_list = np.array(numerator_list), np.array(denominator_list)
    errors =  "\nTotal number of errors encountered: " + str(errors)

    # calculate actual FOS from lists
    factor_of_safety = numerator_list.sum()/ denominator_list.sum()

    # Finish up with so
    results = errors + '\n\nMethod: %s\nCohesion: %d\nEffective Friction Angle: %d\nBulk Density: %d\nNumber of ' \
                       'slices ' \
                       'calculated: %d\nWater Pore Pressure: %d\n\nFactor of Safety: ' % (method,
        soil_cohesion, effective_friction_angle, bulk_density, slice, water_pore_pressure) + str(factor_of_safety)

    f = open('results.log', 'w')
    f.write(results)
    f.close()
    return results
#### /Bishop Method ####
