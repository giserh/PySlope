#!/usr/bin/env python

import numpy as np
from shapely.geometry import LineString, Point, Polygon
import sys, math, itertools
import scipy as sp
import matplotlib.pyplot as plt


class FromConfig(object):
    def __init__(self, config_file):
        self.file_path = config_file
        self.padding = None
        self.delimiter = None
        self.data_file = None
        self.circle_radius = None
        self.baseline = None
        self.soil_cohesion  = None
        self.effective_angle = None
        self.bulk_density = None

    def get_vars(self):
        """
            Function reads config file and returns variables that will be used
            in the program. This is very syntax sensitive so make sure to use exact
            syntax style from comments in config file

            The function ignores lines that start with #
        """
        with open(self.file_path) as f:
            content = f.read().splitlines()

        variables = []
        init_variables = []

        for line in content:
            if not line.startswith('#') and line != '':
                variables.append(line)

        for word in variables:
            entry = word.split()
            if len(entry) < 3:
                print 'Config file - wrong syntax'
                sys.exit()
            key_word = entry[0].lower()
            value    = entry[2]

            if key_word == 'padding':
                self.padding = value
                init_variables.append(self.padding)

            elif key_word == 'delimiter':
                self.delimiter = value
                init_variables.append(self.delimiter)

            elif key_word == 'data_file':
                self.data_file = value
                init_variables.append(self.data_file)

            elif key_word == 'circle_radius':
                self.circle_radius = value
                init_variables.append(self.circle_radius.split(','))

            elif key_word == 'baseline':
                self.baseline = value
                init_variables.append(self.baseline)

            elif key_word == 'soil_cohesion':
                self.soil_cohesion = value
                init_variables.append(self.soil_cohesion)

            elif key_word == 'effective_friction_angle_soil':
                self.effective_angle = value
                init_variables.append(self.effective_angle)

            elif key_word == 'bulk_density':
                self.bulk_density = value
                init_variables.append(self.bulk_density)

        for variable in init_variables:
            if variable is None:
                raise NotImplementedError('Not all variables were set - check config file syntax')

        return self.padding, self.delimiter, self.data_file, \
               self.circle_radius, self.baseline, self.soil_cohesion, self.effective_angle, self.bulk_density



class Calculate(object):

    @staticmethod
    # Create an array of values that span the circumference of a circle from the center point
    def circle_array(x, y, r, elements=360):
        """
        The function takes parameters from a x y position of a circle and generates a full 360 degree coorindate system
        numpy array that outlines the entire circle for radius, r and center x, y
        :param x: X value for center of circle
        :param y: Y value for center of circle
        :param r: Radius value of the circle
        :param elements: this generates the number of elements in the returned list
        :return:
            The function returns a numpy array of side by side (xy) coordinates that outline the circumference
            of the circle
        """
        degrees = np.linspace(0., 360., elements)
        xvalues = np.full_like(degrees, x)
        yvalues = np.full_like(degrees, y)
        rvalues = np.full_like(degrees, r)
        new_x = xvalues + rvalues*np.cos(np.deg2rad(degrees))
        new_y = yvalues + rvalues*np.sin(np.deg2rad(degrees))

        results = np.stack((new_x, new_y), axis=-1)

        return results

    @staticmethod
    def intersections(circ_x, circ_y, circ_radius, p1x, p1y, p2x, p2y):
        """
        Tests to see if two lines intersect with one another and spits out a list
        :param circ_x: x coordinate for a circles center
        :param circ_y: y coordinate for a circles center
        :param circ_radius: a circles radius
        :param p1x: x coordinate for line starting point
        :param p1y: y coordinate for line starting point
        :param p2x: x coordinate for line ending point
        :param p2y: y coordinate for line ending point
        :return:
            return a list object for xy values of intersection point.. if found
        """
        p = Point(circ_x, circ_y)                      # center of circle
        c = p.buffer(circ_radius).boundary             # radius of circle
        l = LineString([(p1x, p1y), (p2x, p2y)])       # line point
        i = c.intersection(l)
        i = np.array(i)
        if i.size != 0:
            return i

    @staticmethod
    def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    @staticmethod
    def arraylinspace(array_1d, num_elements):
        array = array_1d
        num_elements -= 1
        n = num_elements / float(array.size-1)

        x = np.arange(0, n*len(array), n)
        xx = np.arange((len(array) - 1) * n + 1)
        b = np.interp(xx, x, array)
        return b

    @staticmethod
    def rad2degree(rad):
        return rad * 180. / np.pi

    @staticmethod
    def degree2rad(degree):
        return degree * np.pi /180.



def get_intersection_coords(xy_frame, cr):
    if len(xy_frame) != len(circ_coor):
        raise StandardError("xy_frame and circ_coordinates are not the same length")

    x_xy = xy_frame[:,0]
    y_xy = xy_frame[:,1]
    c_x = float(cr[0])
    c_y = float(cr[1])
    c_r = float(cr[2])

    # iterate over circle_coordinates
    intersection_indexes = []
    for index in range(len(x_xy)-1):
        x_1, x_2 = x_xy[index], x_xy[index + 1]
        y_1, y_2 = y_xy[index], y_xy[index + 1]
        result =  Calculate.intersections(c_x, c_y, c_r, x_1, y_1,  x_2, y_2)
        if result is not None:
            result.tolist()
            x_value = result[0]
            for i in range(len(x_xy)-1):
                current, next = x_xy[i], x_xy[i + 1]
                if current < x_value < next:
                    index_value = x_xy.tolist().index(current)
                    intersection_indexes.append(index_value)
    return intersection_indexes

def circle_narrow(circle_coordinates, xy_frame, left_bound, right_bound,  buff=2):
    """

    Takes the circle coordinates and the existing xy_frame with the intersection bounds.
    It then tries to isolate the the circle coordinates to it just encompasses the coordinate sets
    between the two intersection points of the elevation profile
    """
    x_list, y_list = [], []
    for set in circle_coordinates:
        x, y = 0, 1
        if  xy_frame[left_bound][x] <= set[x] <= (xy_frame[right_bound][x]+buff):
            x_list.append(float(set[x]))
            y_list.append(float(set[y]))
    half_circle = np.stack((x_list, y_list), axis=-1)

    x_list = []
    y_list = []
    for set in half_circle:
        x, y = 0, 1

        if  xy_frame[left_bound][y] <= set[y] <= (xy_frame[right_bound][y]):
            x_list.append(float(set[x]))
            y_list.append(float(set[y]))

    x_list, y_list = np.array(x_list), np.array(y_list)
    circ_workspace = np.stack((x_list, y_list), axis=-1)
    return circ_workspace



#### set variables from the configuratoin file
padding, delimter, data_file, \
circle_radius, baseline, soil_cohesion, \
effective_angle, bulk_density = FromConfig('config.txt').get_vars()
bulk_density = float(bulk_density)
effective_angle = float(effective_angle)
soil_cohesion = float(soil_cohesion)
cr = circle_radius.split(',')
####
#
#
#### load data from file as numpy array
data = np.loadtxt(data_file, delimiter=delimter)
####
#
#
#### create numpy array of x values from data
spatial_values = data[:,0]          # x values
xmin = min(spatial_values)
xmax = max(spatial_values)
####
#
#
#### create numpy array of y values from data
elevetaion_values = data[:,1]       # y values
ymin = min(elevetaion_values)
ymax = max(elevetaion_values)
####
#
#
#### create x and y 'frames' consisting of num_of_elements following the
#### data points from the data elevation file
num_of_elements = 100
x_frame = np.linspace(xmin, xmax, num_of_elements)
y_frame = Calculate.arraylinspace(elevetaion_values, num_of_elements)
####
#
#
#### create a 2d numpy array from stacking the x_frame and y_frame
#### generate the coordinates of a perfect circle with supplied
#### arguments making it the same size as the xy_frame
xy_frame = np.stack((x_frame, y_frame), axis=-1)
circ_coor = Calculate.circle_array(cr[0], cr[1], cr[2], elements=num_of_elements)
####
#
#
#### Find the intersection index numbers where the elevation profile
#### intersects with the circle coordinates.
####
intersection_indexes = get_intersection_coords(xy_frame, cr)
left_bound, right_bound = intersection_indexes[0], intersection_indexes[1]
####
#
#
#### create a workspace from slicing the generated xy_frame to encompass
#### only the data points that are within the circle intersections
xy_workspace = np.array((xy_frame.tolist()[left_bound : right_bound]))
####
#
#
#### Take the existing workspace and create same profile with num_of_elements
#### added making the data points more for better calculations
xy_workspace_x, xy_workspace_y = xy_workspace[:,0], xy_workspace[:,1]
xy_workspace_x, xy_workspace_y = Calculate.arraylinspace(xy_workspace_x, num_of_elements), \
                                 Calculate.arraylinspace(xy_workspace_y, num_of_elements)

xy_workspace   = np.stack((xy_workspace_x, xy_workspace_y), axis=-1)

circ_workspace = circle_narrow(circ_coor, xy_frame, left_bound, right_bound)
####
#
#
#### Create a shapely line using the coordinates from circ_workspace
arc = LineString(circ_workspace)
####
#
#
#### Iterate through each point in xy_workspace (left to right)
#### calculating the xy coordinates of the intersection on the arc
#### using shapely.intersection to create a polygon.
#### After a polygon has been formed finding the area will lead
#### to calculating the 'slice' weight and from there the Factor
#### of Saftey can be calcuated which will be stored in a list
#
#
#### Create a iterator using a lists index

#plt.scatter(x_frame, y_frame, color="red")
#plt.scatter(xy_workspace[:,0], xy_workspace[:,1], color="yellow")
#plt.scatter(circ_coor[:,0], circ_coor[:,1])
#plt.scatter(circ_workspace[:,0], circ_workspace[:,1], color="green")
#plt.scatter(cr[0], cr[1])
#plt.show()
# these points - in list shows the intersection points between profile and circular radius

numerator_list = []
denominator_list = []
errors = 0
for index in range(len(xy_workspace)-1):
    try:
        buff = 10**100
        current, next = xy_workspace[index], xy_workspace[index+1]

        # create ambiguous line to be used for intersection calculation
        tempL_line = LineString([current, (current[0], current[1]-buff)])

        # find the intersection coord with the fake line and the arc
        intsec_arc1 =  arc.intersection(tempL_line)

        # create ambiguous line to be used for intersection calculation
        tempR_line = LineString([next, (next[0], next[1]-buff)])

        # find the intersection coord with the fake right line and the arc
        intsec_arc2 = arc.intersection((tempR_line))

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

            print numerator, denominator, effective_angle
            numerator_list.append(numerator)
            denominator_list.append(denominator)
    except:
        errors +=1



print "total number of errors caught: " + str(errors)
numerator_list, denominator_list = np.array(numerator_list), np.array(denominator_list)
print numerator_list.sum()/ denominator_list.sum()
#plt.show()
