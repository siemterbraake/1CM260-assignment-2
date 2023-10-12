# -*- coding: utf-8 -*-
"""
@author: Original template by Rolf van Lieshout and Krissada Tundulyasaree
"""
from copy import deepcopy
import sys
from Location import Location

class Route:
    """
    Class used to represent a route for both the first or second echelon
    vehicles

    Parameters
    ----------
    locations : the route sequence of locations for the vehicles. The first and last index correspond 
        to the depot for the first-echelon route and a satellite for the second-echelon route.
    customers: the set of customers served by the second echelon vehicle. Note the set will be empty for 
        the first echelon vehicle route.
    problem : the problem instance, used to compute distances.
    feasible : true if route respects capacity and their corresponding orgins and destinations.
        For the first-echelon vehicles, the origins and destinations is the depot while it 
        is satellite for the second-echelon vehicles.
    distance : total distance driven, extremely large number if infeasible
    cost: total cost: first echelon include handling, distance cost and vehicle cost while the second echelon
        only has the vehicle and distance cost.
    servedLoad: store the load for each customer / satellite location(s) satisfied by the route
        note that the position in the list correspond to the order of the locations
        for exmaple: locations: [1,2,3,1], servedLoad:[10,20]
        this means that the load of location 2 is 10 and load of location 3 is 20.
    isFirstEchelonRoute: true if the route belongs to the first echelon.
    """

    def __init__(self, locations: list[Location], problem, isFirstEchelonRoute: bool, load: list[int]):
        self.locations = locations
        self.customers = []
        self.problem = problem
        # track the demand for each satellite for the first echelon route
        self.isFirstEchelonRoute = isFirstEchelonRoute
        self.servedLoad = load
        # check the feasibility and compute the distance
        self.feasible = self.isFeasible()
        if self.feasible:
            # compute the distance
            self.distance = self.computeDistance()
            self.cost = self.computeCost()
        else:
            self.distance = sys.maxsize  # extremely large number
            self.cost = sys.maxsize  # extremely large number

    def computeDistance(self) -> float:
        """
        Method that computes and returns the distance of the route
        """
        totDist = 0
        for i in range(1, len(self.locations)):
            prevNode = self.locations[i-1]
            curNode = self.locations[i]
            dist = self.problem.distMatrix[prevNode.nodeID][curNode.nodeID]
            totDist += dist
        return totDist

    def computeCost(self) -> float:    
        """
        Method that computes total cost = load handling cost + vehicle cost + transportation cost

        """
        # Calculate the distance
        self.distance = self.computeDistance()
        toCost = 0
        handling = 0    
        # Calculate the handling cost
        if self.isFirstEchelonRoute is True:
            cost_veh = self.problem.cost_first
            handling += self.problem.cost_handling * sum(self.servedLoad)
        else:
            cost_veh = self.problem.cost_second 
        # Calculate the vehicle cost
        vehicle_cost = cost_veh * len(self.locations)
        # Calculate the total cost
        toCost = handling + self.distance + vehicle_cost
        
        return toCost 

    def __str__(self) -> str:
        """
        Method that prints the route
        """
        s = 'Route '
        for i in self.locations:
            s += f"{i} "
        s += f"cost = {round(self.cost,2)} "
        s += f"load = {self.servedLoad}"
        return s

    def isFeasible(self) -> bool:
        """
        Method that checks feasbility. Returns True if feasible, else False
        """
        if self.isFirstEchelonRoute is True:
            start = [i.nodeID for i in self.problem.depots]
            capacity = self.problem.capacity_first

        else:
            start = [i.nodeID for i in self.problem.satellites]
            capacity = self.problem.capacity_second

        # Check the start and end point of the route
        if start.count(self.locations[0].nodeID) == 0 or start.count(self.locations[-1].nodeID) == 0:
            return False

        curLoad = 0  # current load in vehicle

        if self.isFirstEchelonRoute is False:
            if self.computeDistance() > self.problem.range_second:
                return False

        # iterate over route and check capacity feasibility
        for i in range(1, len(self.locations)-1):
            curLoad += self.servedLoad[i-1]
            if curLoad > capacity:
                return False

        return True

    def removeLocation(self, location: Location) -> tuple[int, int]:
        """
        Method that removes a location from the route.

        Parameters
        ----------
        location : location to be removed.

        Returns
        -------
        location_index :  the index of the location from the list of locations of this vehicle routes.
        """
        # get the index of the deliveryLoc
        location_index = 0
        for index, i in enumerate(self.locations):
            if i.nodeID == location.nodeID:
                location_index = index
                break
        # get the load of the removed location
        load = self.servedLoad[location_index - 1]
        # update the route location
        self.locations.remove(location)
        # the route changes, so update
        self.cost = self.computeCost()
        # remove the servedLoad
        del self.servedLoad[location_index - 1]
        # For the second echelon vehicle, remove the customers.
        if self.isFirstEchelonRoute is False:
            for i in self.customers:
                if location.nodeID == i.deliveryLoc.nodeID:
                    self.customers.remove(i)
                    break

        return location_index, load

    def insertLocation(self, location: Location, load: int, location_index: int):
        """
        Method that inserts a location to the route.

        Parameters
        ----------
        location : location to be inserted.
        load : load for delivery.
        location_index :  the index of the location from the list of locations of this vehicle routes.
        """
        routeCopy = deepcopy(self)
        # update the route location
        routeCopy.locations.insert(location_index, location)
        # the route changes, so update
        routeCopy.cost = self.computeCost()
        # insert the servedLoad
        routeCopy.servedLoad.insert(location_index - 1, load)

        if routeCopy.isFeasible():
            return routeCopy
        else:
            return None

    def greedyInsert(self, location: Location, load: int):
        """
        Method that inserts the location and corresponding load to a route
        that give the shortest total distance. Returns best route. 

        Parameters
        ----------
        location : customers or satellites location for insertion.
        load : load for delivery.

        Returns
        -------
        bestInsert : Route
            Route after insertion.
        """
        minDist = sys.maxsize  # initialize as extremely large number
        bestInsert = None
        # return None if empty is sent.
        if load <= 0:
            return bestInsert
        # iterate over all possible insertion positions
        for i in range(1, len(self.locations)):
            locationsCopy = self.locations.copy()
            demandCopy = self.servedLoad.copy()
            # update demand
            demandCopy.insert(i-1, load)
            locationsCopy.insert(i, location)
            afterInsertion = Route(locationsCopy, self.problem, self.isFirstEchelonRoute, demandCopy)
            # check if insertion is feasible
            if afterInsertion.isFeasible():
                # check if cheapest
                if afterInsertion.distance < minDist:
                    bestInsert = afterInsertion
                    minDist = afterInsertion.distance
        return bestInsert
    
    def findRegret(self, location: Location, load: int) -> tuple[float, float]:
        """
        Method that find the regret value for the location and corresponding load to a route

        Parameters
        ----------
        location : customers or satellites location for insertion.
        load : load for delivery.

        Returns
        -------
        bestCost : the cost of the best insertion
        secondbestCost : the cost of the second best insertion
        """
        curCost = self.cost
        bestCost = sys.maxsize
        secondbestCost = sys.maxsize
        bestRoute = None
        # return None if empty is sent.
        if load <= 0:
            return bestCost-curCost, secondbestCost-curCost, bestRoute
        # iterate over all possible insertion positions
        for i in range(1, len(self.locations)):
            locationsCopy = self.locations.copy()
            demandCopy = self.servedLoad.copy()
            # update demand
            demandCopy.insert(i-1, load)
            locationsCopy.insert(i, location)
            afterInsertion = Route(locationsCopy, self.problem, self.isFirstEchelonRoute, demandCopy)
            # check if insertion is feasible
            if afterInsertion.isFeasible():
                # check if cheapest
                if afterInsertion.cost < bestCost:
                    secondbestCost = bestCost
                    bestCost = afterInsertion.cost
                    bestRoute = afterInsertion
                elif afterInsertion.cost < secondbestCost:
                    secondbestCost = afterInsertion.cost
        return bestCost-curCost, secondbestCost-curCost, bestRoute


    
