#!/usr/bin/env python

from utils import *


def fos(fos, config_file, data_file):
    if fos is None:
        raiseGeneralError("No method chosen: fos --help")
    config = ReadConfig(config_file)
    verbose = True if config.verbose == 'yes' else False
    data = loadProfileData(verbose, data_file, config.num_of_slices, config.delimit)

    if config.perform_critical_slope == 'yes':
        ### recreate all steps via function ##
        perform_critical_slope_sim(verbose, config, data, fos)
        perform_critical_slope_sim(verbose, config, data, 'bishop')
    else:
        ## create shapely circle with circle data
        shapely_circle = createShapelyCircle(verbose,
                                             config.c_x,
                                             config.c_y,
                                             config.c_a,
                                             config.c_b,
                                             config.c_r)

        ## find intersection coordinates of shapely_circle and profile data
        intersection_coordinates = intersec_circle_and_profile(verbose, shapely_circle, data)

        # created normal shapley object from raw profile data
        shapely_elevation_profile = createShapelyLine(verbose, data)

        #### Preview geometery ####
        previewGeometery(config.show_figure, shapely_circle, data)

        ## Using intersection coordinates isolate the section of profile that is within the circle.
        ### Check to see if intersection_coordinates length is 4 elements.. if it isn't so that means for some reason
        # there are more or less than two intersection points in the profile - shouldn't really happen at all...
        int1, int2         = fetchIntersecCoords(verbose, intersection_coordinates)
        circle_coordinates = createNumpyArray(verbose,list(shapely_circle.coords), "Circle/Ellipse")
        elevation_profile  = createNumpyArray(verbose, list(shapely_elevation_profile.coords),'Profile Coordinates')

        # Create sliced array with boundaries from elevation_profile
        sliced_ep_profile = createSlicedElevProfile(verbose,
                                                    elevation_profile,
                                                    config.num_of_slices,
                                                    int1,
                                                    int2)

        ### Perform actual calculation of forces slice-by-slice
        FOS_Method( fos,
                                     sliced_ep_profile,
                                     shapely_circle,
                                     config.bulk_density,
                                     config.soil_cohesion,
                                     config.effective_friction_angle_soil,
                                     config.vslice,
                                     config.percentage_status,
                                     config.water_pore_pressure,
                                     verbose)



        plt.scatter(circle_coordinates[:,0], circle_coordinates[:,1], color='red')
        ep_profile = arraylinspace2d(elevation_profile, config.num_of_slices)
        plt.scatter(ep_profile[:,0], ep_profile[:,1])
        plt.scatter(sliced_ep_profile[:,0], sliced_ep_profile[:,1], color='green')


        if config.save_figure == 'yes':
            verb(verbose, 'Saving result to figure.')
            plt.savefig('slope_profile.tif')



