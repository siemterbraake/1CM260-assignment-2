# -*- coding: utf-8 -*-
"""
@author: Original template by Rolf van Lieshout and Krissada Tundulyasaree
"""
import matplotlib.pyplot as plt
from copy import deepcopy
from Route import Route
from Location import Location
from Customer import Customer
from random import Random


class Solution:
    """
    Method that represents a solution to the 2E-CVRP

    Attributes
    ----------
    problem : the problem that corresponds to this solution
    routes_1 :  Routes for the first echelon vehicle in the current solution
    routes_2 : Routes for the second echelon vehicle the current solution
    served : Customers served in the second echelon vehicle current solution
    notServed : Customers not served in the second echelon vehicle current solution
    distance : total distance of the current solution
    cost:  total cost consisting of handling, distance and vehicle cost.
    handling:  total handling cost of loads at satellites
    satDemandServed : Load served in the first echelon vehicle current solution
    satDemandNotServed : Load not served in the first echelon vehicle current solution
    """

    def __init__(self, problem, routes_2: list[Route], served: list[Customer], notServed: list[Customer]):

        self.problem = problem
        self.routes_2 = routes_2
        self.served = served
        self.notServed = notServed

    def computeDistance(self):
        """
        Method that computes the distance of the solution
        """
        self.distance = 0
        # Calculate the cost for the first echelon
        for routes_1 in self.routes_1:
            self.distance += routes_1.distance
        # Calculate the cost for the second echelon
        for routes_2 in self.routes_2:
            self.distance += routes_2.distance

    def computeCost(self):    
        """
        Method that computes total cost = load handling cost + vehicle cost + transportation cost

        """
        self.computeDistance()
        # Calculate the handling cost
        handling = self.problem.cost_handling * sum(self.satDemandServed)
        # Calculate the vehicle cost
        vehicle_cost = self.problem.cost_first * len(self.routes_1) + self.problem.cost_second * len(self.routes_2)
        # Calculate the total cost
        self.cost = handling + self.distance + vehicle_cost
                   
    def __str__(self)-> str: 
        """
        Method that prints the solution
        """
        # Check the second echelon to generate order for the first echelon
        print(f"First-echelon Solution with Satellite demand {self.satDemandServed}")
        for route in self.routes_1:
            print(route)
                
        nRoutes = len(self.routes_2)
        nNotServed = len(self.notServed)
        print("Second-echelon Solution with "+str(nRoutes)+" routes and "+str(nNotServed)+" unserved customers: ")
        for route in self.routes_2:
            print(route)
            
        s= ""
        
        return s
    
    def executeRandomRemoval(self,nRemove: int, random: Random, firstEchelon: bool):
        """
        Method that executes a random removal of locations
        
        This is destroy method number 1 in the ALNS

        Parameters
        ----------
        nRemove : number of customers that is removed.                 
        randomGen :  Used to generate random numbers        
        firstEchelon: True if choose to remove location from the first-echelon routes
            False otherwise
        """
        if firstEchelon is True:
            routes = self.routes_1
        else:
            routes = self.routes_2
        for _ in range(nRemove):
            # terminate if no more customers/loads are served
            if len(routes)==0: 
                break
            #pick a random customer/load and remove it from the solution
            while True:
                route = random.choice(routes)
                # if the route has loads/customers.
                if len(route.locations) > 2:
                    break
                else:
                    routes.remove(route)
                len_route = [len(i.locations) for i in routes]
                # All routes are empty: no served loads or customers
                if sum(len_route) == 2 * len(routes):
                    break
            if len(route.locations) == 2:
                break
            loc = random.choice(route.locations[1:-1]) 
            self.removeLocation(loc, firstEchelon, route)

    def removeLocation(self,location: Location, firstEchelon: bool, route: Route):
        """
        Method that removes a location from the indicated level of echelon vehicles


        Parameters
        ----------
        location : Location to be removed
        firstEchelon : True if choose to remove location from the first-echelon routes
            False otherwise        
        route : This is the route which have the location to be removed
        """
        
        # Remove the location from the route
        _ , load = route.removeLocation(location)
        if firstEchelon is True:
            # update lists with served and unserved load
            self.satDemandServed[location.nodeID - 1] -= load
            self.satDemandNotServed[location.nodeID - 1] += load
        else:
            # update lists with served and unserved customers
            customer = 0
            for i in self.served:
                if i.deliveryLoc.nodeID == location.nodeID:
                    customer = i
            self.served.remove(customer)
            self.notServed.append(customer)    
    

    def computeDemandSatellites(self):
        """
        Generate a list of total demand for all satellites given the second echelon routes

        """
        # number of satellites
        nSat = len(self.problem.satellites)
        self.satDemandNotServed = [0 for i in range(nSat)]
        # Find total demand for each satellite from the second echelon routes          
        for i in self.routes_2:       
            sat = i.locations[0]
            totalDemand = sum(j.demand for j in i.locations)
            self.satDemandNotServed[sat.nodeID - 1] += totalDemand

    def executeRandomInsertion(self, randomGen: Random):
        """
        Method that contruct randomly the routes for the first and second echelon vehicles by 
        1. randomly insert the customers to create the second echelon routes.
        2. depending on the constructed second echelon routes, randomly insert demand at the
        satellites to construct the first echelon routes.
        
        This is repair method number 1 in the ALNS

        Parameters
        ----------
        randomGen : Used to generate random numbers

        """
        
        self.executeRandomInsertionSecond(randomGen)
        # Based on the second echelon routes, generate the first echelon routes
        self.executeRandomInsertionFirst(randomGen)

    def executeRandomInsertionFirst(self,randomGen: Random):
        """
        Method that randomly inserts the demand of each satellite to construct the routes
        for the first echelon vehciles. Note that we assume given second-echelon routes
        to determine demand of each satellite.
                
        Parameters
        ----------
        randomGen : Used to generate random numbers

        """
        # Determine the first echelon from the given-second echelon routes
        # This is used to reset the existing first-echelon route.
        self.routes_1 = []
        # Derive demands for satellites
        self.computeDemandSatellites()
        # iterate over the list with unserved customers
        self.satDemandServed = [0]*len(self.satDemandNotServed)
        while sum(self.satDemandNotServed) > 0:
            #pick a satellite with some loads for the first echelon vehicle to deliver
            load_max = 0
            while load_max == 0:
                load_max = randomGen.choice(self.satDemandNotServed)
            sat_ID = self.satDemandNotServed.index(load_max)
            # keep track of routes in which this load could be inserted
            potentialRoutes = self.routes_1.copy()
            # potentialRoutes = copy.deepcopy(self.routes_1)
            inserted = False
            while len(potentialRoutes) > 0:
                # pick a random route
                randomRoute = randomGen.choice(potentialRoutes)
                remain_load = self.problem.capacity_first - sum(randomRoute.servedLoad)
                if load_max > remain_load:
                     load = remain_load
                else:
                     load = load_max
                afterInsertion = randomRoute.greedyInsert(
                    self.problem.satellites[sat_ID], load)
                if afterInsertion == None:
                    # insertion not feasible, remove route from potential routes
                    potentialRoutes.remove(randomRoute)
                else:
                    # insertion feasible, update routes and break from while loop
                    inserted = True                   
                    self.routes_1.remove(randomRoute)
                    self.routes_1.append(afterInsertion)
                    break
            # if we were not able to insert, create a new route
            if not inserted:
                # create a new route with the load
                depot = self.problem.depot
                locList = [depot, self.problem.satellites[sat_ID], depot]
                remain_load = self.problem.capacity_first 
                if load_max > remain_load:
                     load = remain_load
                else:
                     load = load_max
                newRoute = Route(locList, self.problem, True, [load])
                # update the demand
                self.routes_1.append(newRoute)
            # update the lists with served and notServed customers
            self.satDemandNotServed[sat_ID] -= load
            self.satDemandServed[sat_ID] += load

    def executeRandomInsertionSecond(self, randomGen: Random):
        """
        Method that randomly inserts the unserved customers in the solution for the second echelon routes.
        
        Parameters
        ----------
        randomGen : Used to generate random numbers

        """
        # iterate over the list with unserved customers
        while len(self.notServed) > 0:
            # pick a random customer
            cust = randomGen.choice(self.notServed)
            # keep track of routes in which customers could be inserted
            potentialRoutes = self.routes_2.copy()
            inserted = False
            while len(potentialRoutes) > 0:
                # pick a random route
                randomRoute = randomGen.choice(potentialRoutes)
                afterInsertion = randomRoute.greedyInsert(
                    cust.deliveryLoc, cust.deliveryLoc.demand)
                if afterInsertion is None:
                    # insertion not feasible, remove route from potential routes
                    potentialRoutes.remove(randomRoute)
                else:
                    # insertion feasible, update routes and break from while loop
                    inserted = True
                    afterInsertion.customers = randomRoute.customers
                    afterInsertion.customers.add(cust)
                    self.routes_2.remove(randomRoute)
                    self.routes_2.append(afterInsertion)
                    break

            # if we were not able to insert, create a new route
            if not inserted:
                # create a new route with the customer
                sat = randomGen.choice(self.problem.satellites)
                locList = [sat, cust.deliveryLoc, sat]
                newRoute = Route(locList, self.problem, False, [cust.deliveryLoc.demand])
                newRoute.customers = {cust}
                self.routes_2.append(newRoute)
            # update the lists with served and notServed customers
            self.served.append(cust)
            self.notServed.remove(cust)

    def executeGreedyInsertion(self, randomGen: Random, pertubation: bool):
        """
        Method that contruct the routes for the first and second echelon vehicles by
        1. Greedy insertion to create the second echelon routes.
        2. depending on the constructed second echelon routes, insert demand at the
        satellites to construct the first echelon routes.
        """	
        self.executeGreedyInsertionSecond(randomGen, pertubation)
        # Based on the second echelon routes, generate the first echelon routes
        self.executeGreedyInsertionFirst(randomGen, pertubation)

    def executeGreedyInsertionFirst(self, randomGen: Random, perturbation: bool):
        """
        Method that performs Greedy insertion to construct the first-level routes.
        """
        # Determine the first echelon from the given-second echelon routes
        # This is used to reset the existing first-echelon route.
        self.routes_1 = []
        # Derive demands for satellites
        self.computeDemandSatellites()
        # Create list of unserved satellites
        unservedSatID = [i+1 for i in range(len(self.satDemandNotServed)) if self.satDemandNotServed[i] > 0]
        # Initialize iterative process
        curCity = 0 # depot
        full = True # this causes a new route to be created
        while len(unservedSatID) > 0:
            # Find the satellite nearest to the current city
            curCity = self.problem.distMatrix[curCity][unservedSatID].argmin()
            # Find the satellite ID
            curCity = unservedSatID[curCity]
            if full:
                # initialize a new route
                depot = self.problem.depot
                locList = [depot, self.problem.satellites[curCity-1], depot]
                remain_load = self.problem.capacity_first 
                if self.satDemandNotServed[curCity-1] > remain_load:
                    load = remain_load
                else:
                    load = self.satDemandNotServed[curCity-1]
                    unservedSatID.remove(curCity)
                    full = False
                curRoute = Route(locList, self.problem, True, [load])
                self.routes_1.append(curRoute)
                # update the demand
                self.satDemandNotServed[curCity-1] -= load
                self.satDemandServed[curCity-1] += load
            else:
                # add the satellite to the current route
                curRoute = self.routes_1[-1]
                load = self.satDemandNotServed[curCity-1]
                afterInsertion = curRoute.greedyInsert(
                    self.problem.satellites[curCity-1], load)
                if afterInsertion == None:
                    full = True
                else:
                    unservedSatID.remove(curCity)
                    self.routes_1.append(afterInsertion)
                    # update the demand
                    self.satDemandNotServed[curCity-1] -= load
                    self.satDemandServed[curCity-1] += load 

    def executeGreedyInsertionSecond(self, randomGen: Random, pertubation: bool):
        """
        Method that performs Greedy insertion to construct the second-level routes
        """
        self.served = list(set(self.problem.customers) - set(self.notServed))
        servedId = [i.ID for i in self.served]

        while len(self.notServed) > 0:
            # select a random unserved customer
            cust = randomGen.choice(self.notServed)
            inserted = False
            
            # Find the route where a Greedy insertion is the cheapest
            costInsert = []
            for route in self.routes_2:
                afterInsertion = route.greedyInsert(
                    cust.deliveryLoc, cust.deliveryLoc.demand)
                if afterInsertion is not None:
                    cost = afterInsertion.cost-route.cost
                    if pertubation:
                        cost += cost*randomGen.uniform(-0.2, 0.2)
                else:
                    cost = float('inf')
                costInsert.append(cost)
            
            # Find the route with the minimum cost and insert the customer
            if len(costInsert) == 0:
                costInsert = [float('inf')]

            # Find the minimum cost
            minCost = min(costInsert)

            # If the cost is higher than the cost of opening a new rout, consider a new route
            if minCost > self.problem.cost_second:   
                # create a new route with the customer
                nSat = len(self.problem.satellites)
                iSat = self.problem.distMatrix[cust.ID][:nSat].argmin()
                sat = self.problem.satellites[iSat]
                locList = [sat, cust.deliveryLoc, sat]
                newRoute = Route(locList, self.problem, False, [cust.deliveryLoc.demand])
                newRoute.customers = {cust}	
                if newRoute.cost < minCost:
                    self.routes_2.append(newRoute)
                    inserted = True

            if not inserted:
                iInsert = costInsert.index(minCost)
                self.routes_2[iInsert] = self.routes_2[iInsert].greedyInsert(
                    cust.deliveryLoc, cust.deliveryLoc.demand)                
            # update the lists with served and notServed customers
            self.notServed.remove(cust)
            self.served.append(cust)
            servedId.append(cust.ID)        

    def executeRegretInsertion(self):
        """
        Method that contruct the routes for the first and second echelon vehicles by regret-2 insertion. 
        First, we insert the customers to create the second echelon routes.
        Second, depending on the constructed second echelon routes, insert demand at the
        satellites to construct the first echelon routes.
        
        This is repair method number 3 in the ALNS
        """
        self.executeRegretInsertionSecond()
        # Based on the second echelon routes, generate the first echelon routes
        self.executeRegretInsertionFirst()

    def executeRegretInsertionFirst(self):
        """
        Method that performs regret-2 insertion to construct the first-level routes.

        """
        pass

    def executeRegretInsertionSecond(self):
        """
        Method that performs regret-2 insertion to construct the second-level routes
        based on the first-level routes.

        """
        pass
    
    def plotRoutes(self, name: str):
        """
        Method that plots the routes
        """
        fig = plt.figure(figsize=(10,10), dpi=400)
        plt.title("Tour")
        # plot the second echelon routes
        for route in self.routes_2:
            for i in range(len(route.locations)-1):
                plt.plot([route.locations[i].xLoc,route.locations[i+1].xLoc],
                         [route.locations[i].yLoc,route.locations[i+1].yLoc],'b')
                # plot the first echelon routes
        for route in self.routes_1:
            for i in range(len(route.locations)-1):
                plt.plot([route.locations[i].xLoc,route.locations[i+1].xLoc],
                         [route.locations[i].yLoc,route.locations[i+1].yLoc],'r')
        # plot the depot
        plt.plot(self.problem.depot.xLoc,self.problem.depot.yLoc,'ko')
        plt.annotate(0, (self.problem.depot.xLoc, self.problem.depot.yLoc))
        # plot the customers
        for i in self.problem.customers:
            plt.plot(i.deliveryLoc.xLoc,i.deliveryLoc.yLoc,'bo')
            plt.annotate(i.ID, (i.deliveryLoc.xLoc, i.deliveryLoc.yLoc))
        # plot the satellites
        for i in self.problem.satellites:
            plt.plot(i.xLoc,i.yLoc,'ro')
            plt.annotate(i.nodeID, (i.xLoc, i.yLoc))
            

        fig.savefig(f"Plots/{name}")

