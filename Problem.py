# -*- coding: utf-8 -*-
"""
@author: Original template by Rolf van Lieshout and Krissada Tundulyasaree
"""

import numpy as np
import sys
from ALNS import ALNS
from Customer import Customer
from Location import Location
        
class TWO_E_CVRP: 
    """
    Class that represents two-echelon capacitated vehicle routing problem
    Attributes
    ----------
    name : name of the instance.
    customers : The set containing all customers.
    customerLoc: the list of all customer locations
    depot : the depot where all the first-echelon vehicles must start and end.
    satellites : the satellites where all the second-echelon vehicles must start and end.
    locations : the set containing all locations: a depot, satellites and customers.
    distMatrix : matrix with all distances between locations
    capacity_first : first-echelon vehicle capacity
    cost_first : first-echelon vehicle cost
    capacity_second : second-echelon vehicle capacity
    cost_second : second-echelon vehicle cost
    cost_handling : handling fee per transshiped unit at satellite     
    """         
    def __init__(self,name: str, customers: list[Customer], customerLoc: list[Location], depots: list[Location], satellites: list[Location]):
        self.name = name
        self.customerLoc = customerLoc
        self.depot = depots[0]
        self.satellites = satellites
        self.customers = customers
        #construct the set for all location
        self.locations = set()
        self.locations.add(self.depot)
        count = 1
        for s in self.satellites:
            s.nodeID = count
            self.locations.add(s)
            count+=1
        for c in self.customerLoc:
            c.nodeID = count
            self.locations.add(c)
            count+=1
        #compute the distance matrix 
        self.distMatrix = np.zeros((len(self.locations),len(self.locations))) #init as nxn matrix
        for i in self.locations:
            for j in self.locations:
                # No connection between Depot and customers
                case_1 = i.nodeID == 0 and j.nodeID > len(self.satellites)
                case_2 = i.nodeID > len(self.satellites) and j.nodeID == 0
                if case_1 or case_2 :
                    distItoJ = sys.maxsize
                else:
                    distItoJ = Location.getDistance(i,j)
                self.distMatrix[i.nodeID,j.nodeID] = distItoJ
        # define problem instance attribute
        # note: These values are based on the Readme-Set8.txt except the cost_handling
        self.capacity_first = 200
        self.cost_first = 50 
        self.capacity_second = 50 
        self.cost_second = 25 
        self.cost_handling = 5 
        
    def __str__(self):
        return f" 2E-CVRP problem {self.name} with {len(self.customerLoc)} customers "

    def readInstance(fileName: str, dir: str = "Must") -> "TWO_E_CVRP":
        # Read filename
        instance_name = fileName[:-4]
        n_satellites = int(instance_name[6])
        n_customers = int(instance_name[8:])
        f = open(f"Instances/{dir}/{fileName}")

        n_line = 0  # count number of line
        nodeCount = 1  # count number of nodes
        customerLoc = []  # store customers-location object
        depot = []  # store the depot location object
        satellites = []  # store the satellite location object
        customers = []  # store customers object 
        for line in f.readlines()[:-1]:
            asList = []
            n = 6
            for index in range(0, len(line), n):
                asList.append(line[index: index + n].strip())

            if line:
                x = int(asList[0])  # need to remove ".0" from the string
                y = int(asList[1])

                if n_line < n_customers:  # For customers
                    demand = int(asList[4])
                    servTime = int(asList[5])
                    typeLoc = -1
                    # This is to renumber the customer ID
                    nodeID = nodeCount + n_satellites
                    customerLoc.append(
                        Location(x, y, demand, servTime, typeLoc, nodeID))
                    cust = Customer(
                        Location(x, y, demand, servTime, typeLoc, nodeID), nodeID)
                    nodeCount += 1
                    customers.append(cust)
                elif n_line >= n_customers and n_line < n_customers + n_satellites:  # For satellites
                    demand = 0
                    servTime = int(asList[2])
                    typeLoc = 1
                    nodeID = nodeCount
                    nodeCount += 1
                    satellites.append(
                        Location(x, y, demand, servTime, typeLoc, nodeID))
                elif n_line == n_customers + n_satellites:  # 1 Depot
                    demand = 0
                    servTime = int(asList[2])
                    typeLoc = 0
                    nodeID = 0
                    depot.append(
                        Location(x, y, demand, servTime, typeLoc, nodeID))
                n_line += 1
        return TWO_E_CVRP(fileName, customers, customerLoc, depot, satellites)

class ProblemSet:
    """
    Class that represents a set of problems
    Attributes
    ----------
    problems : The set containing all problems.
    """
    def __init__(self, instanceList: list[str], dir: str = "Must"):
        self.problems = list()
        for instance in instanceList:
            self.problems.append(TWO_E_CVRP.readInstance(instance, dir))
    
    def runALNS(self, nDestroyOps: int, nRepairOps: int):
        """
        Method that runs the ALNS algorithm for each problem in the set
        """
        for problem in self.problems:
            alns = ALNS(problem, nDestroyOps, nRepairOps)
            alns.execute()
            print(alns.bestSolution)
