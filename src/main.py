#!/usr/bin/env python

from .utils import *
from sys import exit


def main(fos,
         fos_trial,
         soil_cohesion,
         internal_fric,
         num_of_slices,
         water_pore_pres,
         vslice,
         percentage,
         verbose,
         save,
         show,
         do_crit_slope,
         ellipsoid_coordinates,
         delimiter,
         config_file,
         data_file):

	if fos is None:
		General.raiseGeneralError("No method chosen: man fos")
	
	config = ReadConfig(config_file)
	
	if soil_cohesion != -1.1:
		config.soil_cohesion = soil_cohesion
	if delimiter == ',':
		config.delimit = delimiter
	if internal_fric != -1.1:
		config.effective_friction_angle_soil = internal_fric
	if num_of_slices != -1:
		config.num_of_slices = num_of_slices
	if water_pore_pres != -1.1:
		config.water_pore_pressure = water_pore_pres
	if vslice != -1:
		config.vslice = vslice
	if percentage is not None:
		config.percentage_status = percentage.lower()
	if verbose is not None:
		config.verbose = verbose.lower()
	if save is not None:
		config.save_figure = save.lower()
	if show is not None:
		config.show_figure = show.lower()
	if do_crit_slope is not None:
		config.perform_critical_slope = do_crit_slope.lower()
	if ellipsoid_coordinates != '':
		formattedCoords = str(ellipsoid_coordinates.replace(',', ' ')).split()
		if len(formattedCoords) == 4:
			config.circle_coordinates = formattedCoords
			config.c_x = int(formattedCoords[0])    # x
			config.c_y = int(formattedCoords[1])    # y
			config.c_b = int(formattedCoords[2])    # horizontal
			config.c_a = int(formattedCoords[3])    # vertical
			config.c_r = 0
		else:
			General.raiseGeneralError("Wrong Input Format '%s'. More Info: man fos" % ellipsoid_coordinates)

	verbose = True if config.verbose == 'on' else False
	data = Format.loadProfileData(verbose, data_file, config)
	
	if config.perform_critical_slope == 'on':
		### recreate all steps via function ##
		General.previewGeometery(verbose, config, data)
		Perform.perform_critical_slope_sim(False, config, data, fos)
	else:
		
		General.previewGeometery(verbose, config, data)
		## create shapely circle with circle data
		shapely_circle = Create.createShapelyCircle(verbose, config)
		
		## find intersection coordinates of shapely_circle and profile data
		intersection_coordinates = Format.intersec_circle_and_profile(verbose, shapely_circle, data)
		
		# created normal shapley object from raw profile data
		shapely_elevation_profile = Create.createShapelyLine(verbose, data)
				
		## Using intersection coordinates isolate the section of profile that is within the circle.
		### Check to see if intersection_coordinates length is 4 elements.. if it isn't so that means for some reason
		# there are more or less than two intersection points in the profile - shouldn't really happen at all...
		int1, int2 = Format.fetchIntersecCoords(verbose, intersection_coordinates)
		circle_coordinates = Create.createNumpyArray(verbose, list(shapely_circle.coords), "Circle/Ellipse")
		elevation_profile = Create.createNumpyArray(verbose, list(shapely_elevation_profile.coords),
		                                            'Profile Coordinates')
		
		# Create sliced array with boundaries from elevation_profile
		sliced_ep_profile = Create.createSlicedElevProfile(verbose,
		                                                   elevation_profile,
		                                                   config,
		                                                   int1,
		                                                   int2)
		
		### Perform actual calculation of forces slice-by-slice
		Perform.FOS_Method(verbose, fos, config, sliced_ep_profile, shapely_circle, fos_trial)
		
		plt.scatter(circle_coordinates[:, 0], circle_coordinates[:, 1], color='red')
		ep_profile = Format.arraylinspace2d(elevation_profile, config.num_of_slices)
		plt.scatter(ep_profile[:, 0], ep_profile[:, 1])
		plt.scatter(sliced_ep_profile[:, 0], sliced_ep_profile[:, 1], color='green')
		
		if config.save_figure == 'on':
			General.verb(verbose, 'Saving result to figure.')
			plt.savefig('slope_profile.tif')
