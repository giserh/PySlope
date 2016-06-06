    #!/usr/bin/env python

import numpy as np
from shapely.geometry import LineString, Point, Polygon
import sys, math, itertools
import scipy as sp
import matplotlib.pyplot as plt
from utils import *

# Initialize Variables #
delimiter = ''
data_file = ''
soil_cohesion = -1
bulk_density = -1
num_of_elements = -1
effective_friction_angle_soil = -1
show_figure = ''
save_figure = ''
circle_data = ''

### Circle Data ###
c_x = 0.
c_y = 0.
## perfect circle ##
c_r = 0.
## Ellipse ##
c_a = 0.
c_b = 0.

options_from_config = [
        'delimiter',
        'data_file',
        'circle_data'
        'soil_cohesion',
        'effective_friction_angle_soil',
        'bulk_density',
        'num_of_elements',
        'show_figure',
        'save_figure',
    ]

"""To this point"""

class ReadConfig(object):

    def __init__(self, file_name):
        ## General ##
        global delimiter, data_file, soil_cohesion, bulk_density, num_of_elements, show_figure, save_figure

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

    @staticmethod
    def checkCircleData(circle_data):
        an_ellipse = True
        cr = circle_data.split(',')
        if '' in cr:
            sys.exit("Error: Blank space found in: %s" % str(circle_data))

        elif len(cr) == 3:
            # its a perfect circle style x,y,r
            return not an_ellipse

        elif len(cr) == 4:
            # its in ellipse format x,y,(a,b)
            return an_ellipse

        else:
            sys.exit('Something went wrong')

class Calculate(object):

    @staticmethod
    def arraylinspace1d(array_1d, num_elements):
        array = array_1d
        num_elements -= 1
        n = num_elements / float(array.size-1)

        x = np.arange(0, n*len(array), n)
        xx = np.arange((len(array) - 1) * n + 1)
        b = np.interp(xx, x, array)
        return b

    @staticmethod
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

    @staticmethod
    def rad2degree(rad):
        return rad * 180. / np.pi

    @staticmethod
    def degree2rad(degree):
        return degree * np.pi /180.

    @staticmethod
    def slice_array(array2d, intersection_coord_1, intersection_coord_2):
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
        slice_array2d = Calculate.arraylinspace2d(slice_array2d, num_of_elements)

        return slice_array2d

    @staticmethod
    def generateEllipse(c_x,c_y, c_a, c_b):
        x_coords, y_coords = [], []
        degree = 0
        while degree <= 360:
            x = c_x + (c_a*np.cos(Calculate.degree2rad(degree)))
            y = c_y + (c_b*np.sin(Calculate.degree2rad(degree)))
            x_coords.append(x), y_coords.append(y)

            degree += 1

        x_coords, y_coords = np.array(x_coords), np.array(y_coords)
        xy_ellipse = np.stack((x_coords, y_coords), axis=-1)

        return xy_ellipse

#### set variables from the configuratoin file
ReadConfig('config.txt')

effective_angle, angle = effective_friction_angle_soil, effective_friction_angle_soil
####
#
#
#### load data from file as numpy array
data = np.loadtxt(data_file, delimiter=delimiter)
####
#
#### Check to see if num_of_elements is lower than actual length of data:
if num_of_elements < len(data):
    print "Error: You can't have num_of_elements set lower to your total amount of data points" \
          "\n\nTotal Data Points: %s" \
          "\nNum_of_elements: %s" % (str(len(data)), str(int(num_of_elements)))
    sys.exit()
#
## create shapely circle with circle data
#shapely_circle = Point(c_x, c_y).buffer(c_r).boundary

try:
    if c_x is not None or c_y is not None or c_b is not None or c_a is not None:
        ellipse = Calculate.generateEllipse(c_x, c_y, c_a, c_b)
        shapely_circle = LineString(ellipse)
    else:
        sys.exit("Error: c_x, c_y, c_a, c_b not set.. Report bug")
except:
    if c_x is not None or c_y is not None or c_r is not None:
        shapely_circle = Point(c_x, c_y).buffer(c_r).boundary
    else:
        sys.exit("Error: c_x, c_y, c_r not set.. Report bug")
#
#
## create shapely line with elevation profile
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

int1, int2 = (intersection_coordinates[0], intersection_coordinates[1]), (intersection_coordinates[2],
                                                                          intersection_coordinates[3])
#
# Check to see if intersection_1 and intersection_2 are the same. If they are that means the circle only intersects
# the profile once.. not allowed
if int1 == int2:
    print "Error: Circle only intersects the profile in one place - please readjust circle coordinates in config file"
    sys.exit()

circle_coordinates = np.array(list(shapely_circle.coords))
elevation_profile = np.array(list(shapely_elevation_profile.coords))
#plt.scatter(circle_coordinates[:,0], circle_coordinates[:,1], color='red')
#plt.scatter(elevation_profile[:,0], elevation_profile[:,1])
#plt.show()
#
#
# Create sliced array with boundaries from ep_profile
ep_profile = Calculate.arraylinspace2d(elevation_profile, num_of_elements)
sliced_ep_profile = Calculate.slice_array(ep_profile, int1, int2)
#
#
#
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
            effective_angle = Calculate.degree2rad(effective_angle)
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
    soil_cohesion, angle, bulk_density, slice) + str(factor_of_safety)

f = open('results.log', 'w')
f.write(results)
f.close()

print results



plt.scatter(circle_coordinates[:,0], circle_coordinates[:,1], color='red')
plt.scatter(ep_profile[:,0], ep_profile[:,1])
plt.scatter(sliced_ep_profile[:,0], sliced_ep_profile[:,1], color='green')


if save_figure == 'yes':
    plt.savefig('slope_profile.tif')

if show_figure == 'yes':
    plt.show()

