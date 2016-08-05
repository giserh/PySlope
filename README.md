#PySlope v2#

###Who is the program intended for and what is it about?###

The is a CLI slope stability analysis program. Given a set of 2-D x,y values indicating the
profile of a slope the program works out the Factor of Safety of the slope depending on where the circle 
intersects with the elevational profile. 

This program is intended for anyone who is interested in doing slope stability analysis.


###What do I need for this program to work?###

   You will need the following Python Modules for this to work:

   * Numpy
   * Scipy
   * Shapely
   * Matplotlib
   * Click
   
   
   Super Easy Way:
   
   Download the complete python package called: [Anaconda](https://www.continuum.io/downloads)
   This is a brilliant option for scientists who use programming because it comes with pretty much every module you 
   will ever need including the ones required by this program. Highly recommended and great tutorials on how to set 
   that up on your machine - windows/OSX/Linux

    -> Vanilla Conda does not include Click - you must manually download it <-

    	conda install click
   
   
   Medium Way:
        
   If you have a Mac OSX I highly recommend you install [brew] (http://brew.sh/)
   Then it is as simple as:
        
        brew install numpy scipy matplotlib shapely

        -> Click is not availble on brew <-
   
   If you have [pip](https://pip.pypa.io/en/stable/installing/) (which you can test by 
   typing 'pip' in your terminal
    and if you get something else besides):
           
        -bash: pip: command not found
   
   Then you can happily go and install the modules provided by the 'requirements.txt' in main directory:
   
        sudo pip install -r requirements.txt
        
   For windows users - you are out of luck - I am not a windows guy. There are a
    few tutorials online that allow you to install python and the modules itself. If you realized your major mistake 
    by not going with a Unix type OS then have no fear, windows has made some sort of a comeback by using [cygwin]
    (https://www.cygwin.com/)
    
    
   Hard Way:
   
   You can physically go to the homepages of each of the modules and install and compile them yourself. However this 
   is not recommended because you would have to make sure that the modules reside in your PYTHONPATH - NOT
   recommend.


        
### How to use it ###

The program works in two ways - configuring the config.txt (or similiar) and/or using the command line to execute the
different commands. Editing the config.txt file with the parameters you choose. For a step-by-step guide to what each
config option does read on down below under the section 'Configuration File Explained' Once you have everything you need
make sure your **datafile** and **config.txt** are in the same directory. 

A system has been developed where you can now use either the config.txt **AND/OR** command line. Upon successful
installation of the program you can access a more detailed help section in the terminal by:

    man fos

There will be a file called **setup** once downloaded. It is a unix executable file that will install the program to /usr/local
and create all relevant links to be able for use it immediately via commands described below. The setup file also includes other options
including an uninstall feature. More info below. 

    Usage: ./setup [-h] [-u] --Setup Options for Slope Stability Program
    
        where:
            -h    Shows this help message
            -u    Uninstalls all relevant data 
    
            *no argument     
                  Installs relevant data to appropriate folders
    
                
I constantly work on this program and push out major to minor updates. Once you **git clone** the project **git pull** in the same directory.
Once you have the newest version run **setup** again to update the program.

Supported Commands that work out of the box

####fos - factor of safety####

        Usage: fos [OPTIONS] CONFIG_FILE DATA_FILE

          Usage:
        
          fos [-cdnsw] [-e YES/NO] [-m GENERAL/BISHOP] [-o YES/NO] [-p YES/NO] [-v
          YES/NO] [-x YES/NO] [CONFIG_FILE] [DATA_FILE]
        
          Detailed Help: man fos
        
        Options:
          -m [general|bishop]  Specifies Slope Stability Method.
          -s FLOAT             Soil Cohesion in KPa.
          -d FLOAT             Angle of Internal Friction - in degrees -
          -n INTEGER           Number of Slices to Calculate on Slope.
          -w FLOAT             Water Pore Pressure in KPa.
          -c INTEGER           Number of Slice Bulk to Output to Screen - only works
                               if Verbose isturned on, -v
          -p [yes|no]          Display percentage complete.
          -v [yes|no]          Verbose Mode.
          -e [yes|no]          Save Final Figure.
          -o [yes|no]          Show Final Figure.
          -x [yes|no]          Perform Critical Slope Analysis on Data Set.
          -a TEXT              Ellipsoid Coordinates - x,y,h,v
          --help               Show this message and exit.

		


    This program only runs on Python 2.7x


###How does it work?###

Given some basic configuration options the program reads in the configuration file and data from an ambiguous
file of your choosing. It supports: 

* Basic Method of Slicing (General)
* Simplified Bishops Method. 

It reads in elevation data (x,y) coordinates and loads them up into a numpy array. It then generates coordinates of an 
ellipsoid based on the configuration file or terminal input.

It takes both coordinate sets and isolates the points where the circle intersects the profile. For some number
crunching it takes the elevation profile itself and generates a user-defined amount of data points that fits the
profile of the elevation.

This allows for a scientist to gather as few points as possible and letting the computer generate **n** number
of points that simulates a lot of points... After it isolates the 'workspace', then the actual calculation for Factor 
of Safety begins.

After everything is done it will spit out - depending on the verbose setting:

* number of errors caught
* the Factor of Safety of your slope from your given config settings.
* Results can be found in your terminal and results.txt

###Few Pointers###

It has a built in error catching system. It is common as a computer generated values sometimes things don't
go as planned and its impossible to account for each and every problem.. therefore.. when calculating the
factor of saftey and forces for each 'slice' if anything doesn't work out right it completely skips that
slice and move on to the next. It will spit out how many errors it did catch for your information. It only
will give you results on slices that work.

The whole project is documented heavly. If you can contribute to the code I would greatly appreciate it.

It does support a preview of your data with the plotted circle before any calculations are made. This ensures visual confirmation
that the ellipsiod encloses the profile. If the ellipsiod doesn't intersect the profile an error will pop up once you 'continue'.

###What does it not do?###

It does not support multistrata or 3D calculations.


###Configuration File Explained###

The config is very basic and simple. It ignores any line that starts with a '#' and it is very case sensitive.
Each config option has a comment above it showing you exactly how it should be done. Copy it word for work and
just change the values where you see fit. Be warned though unexpected results may happen.. but thats good any
bugs you find email me @ duan_uys@icloud.com

    delimiter = ,
            This option reads your data file and removes the delimiter which by default is ','.
        
            What does this mean?
            If you have a sample set like this:
        
            2,3
            3,4
            4,5
            6,6
        
            Program will load it in a numpy array removing the ',': at this point it only takes one delimiter.
            So:
            
            delimiter = ,(): - Will not work.


    circle_data = 0,0,(1,2) - (x,y,(a,b))
            To provide data for an ellipse supply the argument of:
            (x, y, (a,b)) - without the outside parenthesis
            
            x, y,(a,b) - example
            a = horizontal radius
            b = vertical radius
            
            For a circle simply; a=b

    soil_cohesion = 22 (in kPa)
            Reads in soil cohesion in kPa

    effective_friction_angle_soil = 40 (degrees)
            Internal soil friction maximum angle

    bulk_density = 1760 (Kg/m^3)
            Reads in bulk density of the soil - the program doesn't support multi layered strata yet. It assumes the area 
            is homogenous. Also this is just 2D but hopefully will expand to 3D soon.

    num_of_elements = 100
            This is the number of elements you wish to 'generate' for your eleveation profile. Be warned you may get some
            kind of error if the num_of_elements is lower than the actual total amount of data points you have.
            I also haven't tested it extensivly to see what happens when you really rise that number, but the higher the
            number than theortically it turns the Factor of Saftey into an integral because the length -> 0 of each slice.
            

    ##EXTRA OPTIONS##
            These options does not affect the actual calcuations of the various FOS methods, instead they are more like
            preferences.
            
    water_pore_pressure = 0
            This option takes an only positive integer or 0 that defines the water_pore_pressure of your data. Leave the value at
            0 to neglect water pore pressure in the calculations.

            
    vslices = 100
            This option takes an integer and wraps the different amount of slices calculated into bundles to display 
            to the terminal. vslices = 100 will display to the terminal when 100 slices has been calculated.. This is
             a good option to show the progress. Cannot be 0 or a negative.
             
    percentage_status = on
            This option toggles whether or not you will see a percentage of completion with each slice batch that is 
            completed. This option works jointly with vslices.
    
    show_figure = yes/no
            This option just toggles whether or not you would like the workspace plotted via matplotlib and showed to
            you
    
    
    save_figure = yes/no
            This option toggles whether or not you would like the workspace to be saved as an image in your directory
            Default - .tiff



## Performance Heavy Options ##

    perform_critical_slope = yes/no
            This option toggles whether to perform a critical slope analysis on the given data set and parameters.
            Instead of performing a single Factor of Safety method calculation on the given data set, it performs 
            multiple calculations each time changing the radius of the ellipse/circle, within aspect ratio, and plots
            all curves that achieved below 1. FOS < 1, indicated Driving Force exceeds that of the Resisting Forces.
            