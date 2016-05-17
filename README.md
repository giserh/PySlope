Slope Stability, alpha 1.0

What does it do?

Given some basic configuration options the program reads in the configuration file and data from an ambiguous
file of your choosing. Right now the program only supports very basic - Basic Method of Slicing. It reads the
elevation data (x,y) coordinates and loads them up into a numpy array. It then generates coordinates of a perfect
circle based on the config file where you define your circle.

It takes both coordinate sets and isolates the points where the circle intersects the profile. For some number
crunching it takes the elevation profile itself and generates a user-defined amount of data points that fits the
profile of the elevation.

* This allows for a scientist to gather as few points as possible and letting the computer generate n number
of points that simulates a lot of points...

After it isolates the 'workspace', then the actual calculation for Factor of Safety begins.

* I am not going to go into the logistics if you are interested; follow the source code

After everything is done it will spit out:

* number of errors caught
* the Factor of Safety of your slope from your given config settings.
* Results can be found in your terminal and results.log

Few Pointers

* It has a built in error catching system. It is common as a computer generated values sometimes things don't
 go as planned and its impossible to account for each and every problem.. therefore.. when calculating the
 factor of saftey and forces for each 'slice' if anything doesn't work out right it completely skips that
 slice and move on to the next. It will spit out how many errors it did catch for your information. It only
 will give you results on slices that work.

* Play around with the circle coordinates, it will only catch the coordinates of the elevation profile that
is 'trapped' in the circle and perform calculation on those

* The main.py is documented.. quite heavly... if you can contribute to the code I would greatly appreciate it.
* It does offer some methods for you to plot results using matplotlib.. by default it will plot your entire area
  in different
  colors to see how everything plays out.


What does it not do?

It is a very basic program thus far. I have tried a few circle coordinates, but not every possibility. Most
likely it will find a bug eventually...


What do I need for this program to work?

   You will need the following Python Modules for this to work:

   * Numpy
   * Scipy
   * Shapely
   * matplotlib


Configuration File Explained

The config is very basic and simple. It ignores any line that starts with a '#' and it is very case sensitive.
Each config option has a comment above it showing you exactly how it should be done. Copy it word for work and
just change the values where you see fit. Be warned though unexpected results may happen.. but thats good any
bugs you find email me @

duan_uys@icloud.com

delimiter = ','

This option reads your data file and removes the delimiter which by default is ','.

What does this mean?

If you have a sample set like this:

    2,3
    3,4
    4,5
    6,6

Program will load it in a numpy array removing the ',': at this point it only takes one delimiter.
So this WON'T work

    delimiter =',()'
            alter your data file if need be

    data_file = slope_profile.elev
            This option is simple.. just type in the file name of your raw data.. without any quotes.

    circle_radius = 0,0,3 (x,y, radius) - meters
            This option reads in the circle coordinates, default units are meters

    soil_cohesion = 22 (in kPa)
            Reads in soil cohesion in kPa

    effective_friction_angle_soil = 40 (degrees)
            Reads in the effective friction angle of the soil.. this is the angle that will be used in:

        N tan(effective_friction_angle_soil) - ul

    bulk_density = 1760 (Kg/m^3)
            Reads in bulk density of the soil - the program doesn't support multi layered strata yet. It assumes the area of
            interest if homogenous. Also this is just 2D but hopefully will expand to 3D soon.

    num_of_elements = 100
            This is the number of elements you wish to 'generate' for your eleveation profile. Be warned you may get some
            kind of error if the num_of_elements is lower than the actual total amount of data points you have.
            I also haven't tested it extensivly to see what happens when you really rise that number, but the higher the
            number than theortically it turns the Factor of Saftey into an integral because the length -> 0 of each slice.
            
    show_figure = yes/no
            This option just toggles whether or not you would like the workspace plotted via matplotlib and showed to
             you
    
    
    save_figure = yes/no
            This option toggles whether or not you would like the workspace to be saved as an image in your directory
            Default - .tiff

