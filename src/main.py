#!/usr/bin/env python

from .utils import *

def main(fos, config_file, data_file):
    if fos is None:
        General.raiseGeneralError("No method chosen: fos --help")
    config = ReadConfig(config_file)
    verbose = True if config.verbose == 'yes' else False
    data = Format.loadProfileData(verbose, data_file, config.num_of_slices, config.delimit)

    if config.perform_critical_slope == 'yes':
        ### recreate all steps via function ##
        General.previewGeometery(config.show_figure,Create.createShapelyCircle(verbose,
                                                                config.c_x,
                                                                config.c_y,
                                                                config.c_a,
                                                                config.c_b,
                                                                config.c_r), data)
        Perform.perform_critical_slope_sim(verbose, config, data, fos)
    else:
        ## create shapely circle with circle data
        shapely_circle = Create.createShapelyCircle(verbose,
                                             config.c_x,
                                             config.c_y,
                                             config.c_a,
                                             config.c_b,
                                             config.c_r)

        ## find intersection coordinates of shapely_circle and profile data
        intersection_coordinates = Format.intersec_circle_and_profile(verbose, shapely_circle, data)

        # created normal shapley object from raw profile data
        shapely_elevation_profile = Create.createShapelyLine(verbose, data)

        #### Preview geometery ####
        General.previewGeometery(config.show_figure, shapely_circle, data)

        ## Using intersection coordinates isolate the section of profile that is within the circle.
        ### Check to see if intersection_coordinates length is 4 elements.. if it isn't so that means for some reason
        # there are more or less than two intersection points in the profile - shouldn't really happen at all...
        int1, int2         = Format.fetchIntersecCoords(verbose, intersection_coordinates)
        circle_coordinates = Create.createNumpyArray(verbose,list(shapely_circle.coords), "Circle/Ellipse")
        elevation_profile  = Create.createNumpyArray(verbose, list(shapely_elevation_profile.coords),'Profile Coordinates')

        # Create sliced array with boundaries from elevation_profile
        sliced_ep_profile = Create.createSlicedElevProfile(verbose,
                                                    elevation_profile,
                                                    config.num_of_slices,
                                                    int1,
                                                    int2)

        ### Perform actual calculation of forces slice-by-slice
        Perform.FOS_Method( fos,
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
        ep_profile = Format.arraylinspace2d(elevation_profile, config.num_of_slices)
        plt.scatter(ep_profile[:,0], ep_profile[:,1])
        plt.scatter(sliced_ep_profile[:,0], sliced_ep_profile[:,1], color='green')


        if config.save_figure == 'yes':
            General.verb(verbose, 'Saving result to figure.')
            plt.savefig('slope_profile.tif')



