import sys
import numpy as np
from utils import *
from shapely.geometry import LineString, Point, Polygon

#### Basic Utils ####

def verb(v, string):
    if v:
        print '-> %s' % string


def contains(character, string):
    equals = 0
    for char in string:
        if char == character:
            equals += 1
    if equals == 0:
        return False
    else:
        return True

def raiseGeneralError(arg):
    with open('err.log', "a") as errlog:
        errlog.write("Error: %s\n" % arg)
    sys.exit(arg)


def isInt(value):
    try:
        return int(value)
    except:
        return False
def isFloat(value):
    try:
        return float(value)
    except:
        return False
def isString(value):
    try:
        return str(value)
    except:
        return False

def hasComma(value):
    for index in range(len(value)-1):
        current, next = value[index], value[index+1]
        if current == ',' or next == ',':
            return True
        else:
            return False

def rad2degree(rad):
    return rad * 180. / np.pi

def degree2rad(degree):
    return degree * np.pi /180.

def printslice(slice, vslice, percentage_status, sliced_ep_profile):
    if slice % vslice == 0:
        print 'Calculating Slice: %s %s' % (str(slice), display_percentage_status(  percentage_status,
                                                                                    sliced_ep_profile.size,
                                                                                    slice))
        slice += 1
        return slice

#### /Basic Utils ####


#### Geometry Utils ####
def isEllipse(value):
    if hasComma(value):
        for char in value:
            if char == "(" or char == ")":
                return True
        return False

def generateEllipse(c_x,c_y, c_a, c_b):
        x_coords, y_coords = [], []
        degree = 0
        while degree <= 360:
            x = c_x + (c_a*np.cos(degree2rad(degree)))
            y = c_y + (c_b*np.sin(degree2rad(degree)))
            x_coords.append(x), y_coords.append(y)

            degree += 1

        x_coords, y_coords = np.array(x_coords), np.array(y_coords)
        xy_ellipse = np.stack((x_coords, y_coords), axis=-1)

        return xy_ellipse
#### /Geometry Utils ####

#### Data Formatting Utils ####
def formatCircleData(coordinates):
    results = []

    coordinates = coordinates.replace(',', ' ')
    coordinates = coordinates.replace('(', '')
    coordinates = coordinates.replace(')', '')

    for element in coordinates.split():
        results.append(element)

    if len(results) > 4:
        raiseGeneralError("There are too many data points for your ellipse. Check config file")
    elif len(results) < 3:
        raiseGeneralError("There are too few data points for your circle/ellipse. Check config file.")
    else:
        return results


def arraylinspace1d(array_1d, num_elements):
    array = array_1d
    num_elements -= 1
    n = num_elements / float(array.size-1)

    x = np.arange(0, n*len(array), n)
    xx = np.arange((len(array) - 1) * n + 1)
    b = np.interp(xx, x, array)
    return b

def arraylinspace2d(array_2d, num_elements):
    array_x = array_2d[:,0]
    array_y = array_2d[:,1]
    num_elements -= 1

    n = num_elements / float(array_x.size-1)

    x = np.arange(0, n*len(array_x), n)
    xx = np.arange((len(array_x) - 1) * n + 1)
    fin_array_x = np.interp(xx, x, array_x)

    y = np.arange(0, n*len(array_y), n)
    yy = np.arange((len(array_y) - 1) * n + 1)
    fin_array_y = np.interp(yy, y, array_y)
    ## stack them
    fin_array = np.stack((fin_array_x, fin_array_y), axis=-1)
    return fin_array


def slice_array(array2d, intersection_coord_1, intersection_coord_2, num_of_elements):
        """
        :param array2d: Takes only numpy 2d array
        :param intersection_coord_1: a tuple, list of intersection coordinate
        :param intersection_coord_2: a tuple, list of intersection coordinate
        :return: returns a sliced numpy array within the boundaries of the given intersection coordinates
        """
        int1, int2 = intersection_coord_1, intersection_coord_2
        ## Iterate through array of 2d and find the coordinates the are the closest to the intersection points:
        boundary_list, first_time = [], True
        for index in range(len(array2d)-1):
            current, next        = array2d[index], array2d[index+1]
            current_x, current_y = current[0], current[1]
            next_x, next_y       = next[0], next[1]
            int1x, int1y, int2x, int2y = int1[0], int1[1], int2[0], int2[1]

            # Check to see if current and next elements are in between the coordinates of the intersections
            # store the results in a list


            if current_x < int1x < next_x or current_x < int2x < next_x:
                if not first_time:
                    #boundary_list.append(current.tolist())
                    boundary_list.append(index)
                    first_time = False
                else:
                    #boundary_list.append(next.tolist())
                    boundary_list.append(index+1)


        # Check to see if boundary_list is greater or less than 2: if so something went wrong
        if len(boundary_list) != 2:
            print "Error: Too many/not enough elements in boundary_list - please report this to " \
                  "duan_uys@icloud.com\nNumber of Elements: %d" % len(boundary_list)
            sys.exit()
        left_boundary, right_boundary = boundary_list[0], boundary_list[1]

        # Slice the data to contain the coordinates of the values from array2d
        slice_array2d = array2d[left_boundary : right_boundary]

        # reconstruct slice_array2d to contain = num_of_elements
        slice_array2d = arraylinspace2d(slice_array2d, num_of_elements)

        return slice_array2d


def display_percentage_status(percentage_status, size, slice):
    if percentage_status:
        num_elements = float(size/2)
        perc = (slice /num_elements) * 100

        return " | (%d%%)" % perc
    else:
        return ''

#### /Formatting Utils ####


#### Calculation Utils ####
def FOS_calc_general(water_pore_pressure, mg, degree, effective_angle, cohesion, length):
    denominator  = mg * np.sin(degree)

    if water_pore_pressure == 0:
        numerator = (mg*np.cos(degree))*np.tan(effective_angle) + (cohesion*length)
    elif water_pore_pressure > 0:
        numerator = cohesion*length + (mg*np.cos(degree)-water_pore_pressure*length)*np.tan(effective_angle)
    else:
        raiseGeneralError("water_pore_pressure is a negative number!!!: %s" % water_pore_pressure)

    return numerator, denominator


def isolate_slice(index,
                  sliced_ep_profile,
                  shapely_circle,
                  bulk_density,
                  soil_cohesion):
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
        return length, degree, mg, cohesion

#### /Calculation Utils ####