import numpy as np
from utils import *
from shapely.geometry import LineString, Point, Polygon

def calculateFOS(sliced_ep_profile, shapely_circle, bulk_density, soil_cohesion, effective_friction_angle):
    """

    :param sliced_ep_profile: a numpy array of the profile that is in the circle of interest
    :param shapely_circle:  a shapely object linestring that has the coorindates of the circle/ellipse
    :param bulk_density:    an integer for bulk_density of the soil
    :param soil_cohesion:   an integer for soil_cohesion of the soil
    :param effective_friction_angle: an integer in degrees of the effective angle of friction
    :return:
        returns a single float number of the calculated factor of safety from the given parameters
    """
    effective_angle = effective_friction_angle

    ### Some checks to see if parameters passed are the right objects ###
    if sliced_ep_profile.ndim != 2:
        raiseGeneralError("Numpy array is wrong size, %d, needs to be 2" % sliced_ep_profile.ndim)

    if not isinstance(shapely_circle, LineString):
        raiseGeneralError("Shapely_circle is somehow not a LineString object")

    if not isInt(bulk_density):
        raiseGeneralError("Bulk Density is somehow not an integer")
    if not isInt(soil_cohesion):
        raiseGeneralError("Bulk Density is somehow not an integer")
    if not isInt(effective_friction_angle):
        raiseGeneralError("Bulk Density is somehow not an integer")

    ### Perform actual calculation of forces slice-by-slice
    numerator_list = []
    denominator_list = []
    errors = 0
    slice = 1
    for index in range(len(sliced_ep_profile)-1):
        try:
            buff = 10**100
            current, next = sliced_ep_profile[index], sliced_ep_profile[index+1]

            # create ambiguous line to be used for intersection calculation
            tempL_line = LineString([current, (current[0], current[1]-buff)])

            # find the intersection coord with the fake line and the arc
            intsec_arc1 =  shapely_circle.intersection(tempL_line)

            # create ambiguous line to be used for intersection calculation
            tempR_line = LineString([next, (next[0], next[1]-buff)])

            # find the intersection coord with the fake right line and the arc
            intsec_arc2 = shapely_circle.intersection((tempR_line))

            # create actual polygon using the dimensions if and only if boundaries are set
            if not intsec_arc1.is_empty and not intsec_arc2.is_empty:
                # try to get the angle of the slope using trignometry

                int1_x, in1t_y = intsec_arc1.bounds[0], intsec_arc1.bounds[1]
                int2_x, in2t_y = intsec_arc2.bounds[2], intsec_arc2.bounds[3]
                hypotenuse = LineString([(int1_x, in1t_y), (int2_x, in2t_y)]).length

                tempH_line = LineString([(int2_x, in2t_y), (int2_x-buff, in2t_y)])

                temp_coor = tempL_line.intersection(tempH_line)
                base = LineString([temp_coor, (int2_x, in2t_y)]).length
                length = LineString([(int1_x, in1t_y), (int2_x, in2t_y)]).length

                degree = np.arccos(base/hypotenuse)
                # For explanation on this piece of code:
                # https://github.com/Toblerity/Shapely/issues/21
                # Points and Coordinates are different things in Shapely
                # You have to work around that to use Points to construct
                # a Polygon
                curr, nx = Point(current), Point(next)
                int1, int2 = Point(int1_x, in1t_y), Point(int2_x, in2t_y)
                points = [int1, curr, nx, int2]
                coords = sum(map(list, (p.coords for p in points)), [])
                polygon = Polygon(coords)
                #
                # find the area of the polygon
                area = polygon.area
                # Find the weight of the slab:
                mg = area* bulk_density
                cohesion = soil_cohesion
                # calculate the Factor of Safety:
                #numerator = cohesion*length + (mg*np.cos(degree)-u*length)*np.tan(effective_angle) NOT INCLUDE WATER PORE
                # PRESSURE
                effective_angle = degree2rad(effective_angle)
                numerator = (mg*np.cos(degree))*np.tan(effective_angle) + (cohesion*length)
                denominator  = mg * np.sin(degree)

                numerator_list.append(numerator)
                denominator_list.append(denominator)
                if slice % 100 == 0:
                    print 'Calculating Slice: ' + str(slice)
                slice +=1
        except:
            errors +=1


    numerator_list, denominator_list = np.array(numerator_list), np.array(denominator_list)
    errors =  "\nTotal number of errors encountered: " + str(errors)
    factor_of_safety = numerator_list.sum()/ denominator_list.sum()

    results = errors + '\n\nCohesion: %d\nEffective Friction Angle: %d\nBulk Density: %d\nNumber of slices ' \
                       'calculated: %d\n\nFactor of Safety: ' % (
        soil_cohesion, effective_friction_angle, bulk_density, slice) + str(factor_of_safety)
    return results