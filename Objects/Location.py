from math import sqrt

class Location:
    """
    Class that represents either (i) a location where a customer should be delivered
    (ii) the depot for the first-echelon vehicles (iii) satellites for the second-echelon vehicles
    Attributes
    ----------
    xLoc : int
        x-coordinate.
    yLoc : int
        y-coordinate.
    demand : int
        demand quantity. For depot and satellites, demand is 0.
    servTime : int
        service time. (Extra. Don't consider in the problem)
    typeLoc : int
        1 if satellites, -1 if customers, 0 if depot
    nodeID : int
        id of the node, used for the distance matrix
    """

    def __init__(self, xLoc, yLoc, demand, servTime, typeLoc, nodeID):

        self.xLoc = xLoc
        self.yLoc = yLoc
        self.demand = demand
        self.servTime = servTime
        self.typeLoc = typeLoc
        self.nodeID = nodeID

    def __str__(self):
        """
        Method that prints the location
        """
        return f"({self.nodeID} ,{self.typeLoc})"

    def getDistance(l1,l2):
        """
        Method that computes the rounded euclidian distance between two locations
        """
        dx = l1.xLoc-l2.xLoc
        dy = l1.yLoc-l2.yLoc
        return sqrt(dx**2+dy**2)