Instances of the 2E-VRPTW (Sluijk et al. 2023)

You must run and report the instances in the "Must" folder. The "Optional" folder contains additional instances which you can run if you want to perform additional analyses or consider an extensions. 

This instances set includes different instances with:

	4 different number of customers: 15, 30, 50, 100. 
	3 different combinations of number of depots and satellites: 2 depots and 3 satellites, 3 depots and 5 satellites, 6 depots and 4 satellites 
	4 different categories: Ca, Cb, Cc, Cd

Each instance is represented by a notation which consists of the associated category name, an index, number of depots, number of satellites and number of customers.
For example, "Ca3,2,3,15" denotes the third instance of the category "Ca", with 2 depots, 3 satellites and 15 customers.

The categories Ca,Cb,Cc,Cd are different in terms of time window and demands. Note that Instance set Cc and Cd will only be relevant if the time windows are considered.
See more detailed regarding the instance description in Dellaert et al. (2019).

Each text file contains:

	For each customer: x coordinate, y coordinate, start of time window, end of time window, demand size, service time
	For each satellite: x coordinate, y coordinate, service time
	For each depot: x coordinate, y coordinate, service time

Note that, the Vehicle capacity and cost for all instances are as follows:
	Urban vehicle capacity=200 
	Urban vehicle cost=50
	City freighter capacity=50 
	City freighter cost=25


References:
1. N. Dellaert, F. Dashty Saridarq, T. Van Woensel, and T. G. Crainic. Branch-and-price–based
algorithms for the two-echelon vehicle routing problem with time windows. Transportation
Science, 53(2):463–479, 2019.
2. N. Sluijk, A. M. Florio, J. Kinable, N. Dellaert, and T. Van Woensel. Two-echelon vehicle
routing problems: A literature review. European Journal of Operational Research, 304(3):
865–886, 2023.

