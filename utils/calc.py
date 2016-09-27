import numpy as np
from shapely.geometry import LineString, Point, Polygon

def isolate_slice(index, config, sprofile, circle):
	buff = 10 ** 100
	current, next = sprofile[index], sprofile[index + 1]
	
	# create ambiguous line to be used for intersection calculation
	tempL_line = LineString([current, (current[0], current[1] - buff)])
	
	# find the intersection coord with the fake line and the arc
	intsec_arc1 = circle.intersection(tempL_line)
	
	# create ambiguous line to be used for intersection calculation
	tempR_line = LineString([next, (next[0], next[1] - buff)])
	
	# find the intersection coord with the fake right line and the arc
	intsec_arc2 = circle.intersection((tempR_line))
	
	# create actual polygon using the dimensions if and only if boundaries are set
	if not intsec_arc1.is_empty and not intsec_arc2.is_empty:
		# try to get the angle of the slope using trignometry
		
		int1_x, in1t_y = intsec_arc1.bounds[0], intsec_arc1.bounds[1]
		int2_x, in2t_y = intsec_arc2.bounds[2], intsec_arc2.bounds[3]
		
		prof1_x, prof1_y = current[0], current[1]
		prof2_x, prof2_y = next[0], next[1]
		
		# two calculations for hyptenuse 1) uses bottom of polygon -intersections with arc
		# 2) uses top of polygon - profile coordinates
		arc_hypotenuse = LineString([(int1_x, in1t_y), (int2_x, in2t_y)]).length
		prof_hypotenuse = LineString([(prof1_x, prof1_y), (prof2_x, prof2_y)]).length
		
		arc_tempH_line = LineString([(int2_x, in2t_y), (int2_x - buff, in2t_y)])
		prof_tempH_line = LineString([(prof1_x, prof1_y), (prof1_x + buff, prof1_y)])
		
		arc_temp_coor = tempL_line.intersection(arc_tempH_line)
		prof_temp_coor = tempL_line.intersection(prof_tempH_line)
		
		arc_base = LineString([arc_temp_coor, (int2_x, in2t_y)]).length
		prof_base = LineString([(prof1_x, prof1_y), prof_temp_coor]).length
		
		arc_length = LineString([(int1_x, in1t_y), (int2_x, in2t_y)]).length
		prof_length = LineString([(prof1_x, prof1_y), (prof2_x, prof2_y)]).length
		
		arc_degree = np.arccos(arc_base / arc_hypotenuse)
		prof_degree = np.arccos(prof_base / prof_hypotenuse)
		
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
		mg = area * config.bulk_density
		
		return arc_length, arc_degree, mg, prof_length, prof_degree
