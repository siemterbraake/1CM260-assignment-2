from Location import Location

class Customer:
    """
    Class that represents a customer with its location and nodeID

    Attributes
    ----------

    deliveryLoc : The delivery location.
    ID : id of customer.

    """

    def __init__(self, deliveryLoc: Location, ID: int):

        self.deliveryLoc = deliveryLoc
        self.ID = ID

    def __str__(self):
        """
        Method that prints the customer ID and the delivery location
        """
        return f"({self.ID} ,{self.deliveryLoc})"