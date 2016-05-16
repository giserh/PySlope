{\rtf1\ansi\ansicpg1252\cocoartf1404\cocoasubrtf340
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
\paperw11900\paperh16840\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 Process\
\
1) The program first reads the config.txt file to extract all important information\
2) Next, the program reads the actual data (x,y) values of the profile slope\
3) Separates the x and y values into different lists so it can do different calculations for each\
4) Creates x and y array of n elements that follow the general trend from the data file\
	- This is the tough part because it forces the program to not just alter the already made array,\
	  but instead create a completely new one and use calculated values to create a \
          psuedo-profile of both x and y values\
\
5 ) The next portion tries to find two seperate coordinates where the predefined circle intersects the given profile and stores it in a list object\
\
6 ) Next the program tries to find the boundaries of the calculated array\'92s where all the work will be done. This is accomplished by finding the index value from the calculated arrays both x and y using the intersection coordinates from step 5)\
\
7 ) The program then splits the calculated array so that it contains only values found in 6)\
\
8 ) The resulting x and y arrays are then combined into a 2d numpy array\
\
9) The xy_working space array is then used to coordinate by coordinate to construct a polygon where the area should be calculated. From there we can begin the actual process of calculating the Factor of saftey\
\
10) }