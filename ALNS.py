# -*- coding: utf-8 -*-
"""
@author: Original template by Rolf van Lieshout and Krissada Tundulyasaree
"""
from Solution import Solution
from random import Random
import copy
import time


class Parameters:
    """
    Class that holds all the parameters for ALNS
    """
    nIterations = 10  # number of iterations of the ALNS
    minSizeNBH = 1  # minimum neighborhood size
    maxSizeNBH = 45  # maximum neighborhood size
    randomSeed = 1  # value of the random seed
    # can add parameters such as cooling rate etc.


class ALNS:
    """
    Class that models the ALNS algorithm. 

    Parameters
    ----------
    problem : The problem instance that we want to solve.
    nDestroyOps : number of destroy operators.
    nRepairOps :  number of repair operators.
    wDestroyOps : weight of destroy operator.
    wRepairOps : weight of repair operator.
    randomGen :  random number generator
    currentSolution : The current solution in the ALNS algorithm
    bestSolution : The best solution currently found
    bestCost : Cost of the best solution

    """
    def __init__(self,problem, nDestroyOps: int, nRepairOps: int):
        self.problem = problem
        self.nDestroyOps = nDestroyOps
        self.nRepairOps = nRepairOps
        self.wDestroyOps = [1]*nDestroyOps #initially all destroy operators have weight 1
        self.wRepairOps = [1]*nRepairOps #initially all repair operators have weight 1
        self.wLambda = 0.5 #parameter that controls the sensitivity of the weights
        self.randomGen = Random(Parameters.randomSeed) #used for reproducibility
        
    def constructInitialSolution(self):
        """
        Method that constructs an initial solution using random insertion
        """
        self.currentSolution = Solution(self.problem,list(),list(),list(self.problem.customers.copy()))
        # Generate the second-echelon and first echelon routes by random insertion
        self.currentSolution.executeRandomInsertion(self.randomGen)
        # Calculate the cost
        self.currentSolution.computeCost()
        self.bestSolution = copy.deepcopy(self.currentSolution)
        self.bestCost = self.currentSolution.cost
        print("Created initial solution with cost: "+str(self.bestCost))
        
    def execute(self):
        """
        Method that executes the ALNS
        """
        starttime = time.time() # get the start time
        self.constructInitialSolution()
        for i in range(Parameters.nIterations):
            #copy the current solution
            self.tempSolution = copy.deepcopy(self.currentSolution)
            #decide on the size of the neighbourhood
            sizeNBH = self.randomGen.randint(Parameters.minSizeNBH,Parameters.maxSizeNBH)
            #decide on the destroy and repair operator numbers
            destroyOpNr = self.determineDestroyOpNr()
            repairOpNr = self.determineRepairOpNr()
            #execute the destroy and the repair and evaluate the result
            self.destroyAndRepair(destroyOpNr, repairOpNr, sizeNBH)
            # Determine the first echelon route using the Greedy insertion
            self.tempSolution.computeCost()
            print("Iteration "+str(i)+": Found solution with cost: "+str(self.tempSolution.cost))
            #determine if the new solution is accepted
            score = self.checkIfAcceptNewSol()
            #update the ALNS weights
            self.updateWeights(destroyOpNr, repairOpNr, score)
        endtime = time.time() # get the end time
        cpuTime = round(endtime-starttime)

        print("Terminated. Final cost: "+str(self.bestSolution.cost)+", cpuTime: "+str(cpuTime)+" seconds")
    
    def checkIfAcceptNewSol(self):
        """
        Method that checks if we accept the newly found solution

        Returns
        -------
        score: 0 if we reject the solution, 1 if we accept the solution, 2 if we accept the solution and it is the new global best solution
        """
        # if we found a global best solution, we always accept
        if self.tempSolution.cost < self.bestCost:
            self.bestCost = self.tempSolution.cost
            self.bestSolution = copy.deepcopy(self.tempSolution)
            self.currentSolution = copy.deepcopy(self.tempSolution)
            print("Found new global best solution.")
            score = 2
            return score
        
        # currently, we only accept better solutions, no simulated annealing
        if self.tempSolution.cost<self.currentSolution.cost:
            self.currentSolution = copy.deepcopy(self.tempSolution)
            score = 1
            return score
        
        # if we did not accept the new solution, we do not update the current solution
        score = 0
        return score
    
    def updateWeights(self, destroyOpNr: int, repairOpNr: int, score: int, decay: float = 0.95):
        """
        Method that updates the weights of the destroy and repair operators
        """
        self.wDestroyOps[destroyOpNr-1] = self.wLambda*self.wDestroyOps[destroyOpNr-1] + (1-self.wLambda)*score
        self.wRepairOps[repairOpNr-1] = self.wLambda*self.wRepairOps[repairOpNr-1] + (1-self.wLambda)*score
        self.wLambda = self.wLambda*decay #update the lambda parameter
    
    def determineDestroyOpNr(self) -> int:
        """
        Method that determines the destroy operator that will be applied. 
        Currently we just pick a random one with equal probabilities. 
        Could be extended with weights
        """
        return self.randomGen.choices(range(1,self.nDestroyOps+1),weights=self.wDestroyOps,k=1)[0]
    
    def determineRepairOpNr(self) -> int:
        """
        Method that determines the repair operator that will be applied. 
        Currently we just pick a random one with equal probabilities. 
        Could be extended with weights
        """
        return self.randomGen.choices(range(1,self.nRepairOps+1),weights=self.wRepairOps,k=1)[0]
    
    def destroyAndRepair(self, destroyHeuristicNr: int, repairHeuristicNr: int, sizeNBH: int):
        """
        Method that performs the destroy and repair. More destroy and/or
        repair methods can be added

        Parameters
        ----------
        destroyHeuristicNr : number of the destroy operator.
        repairHeuristicNr : number of the repair operator.
        sizeNBH : size of the neighborhood.

        """
        #perform the destroy 
        if destroyHeuristicNr == 1:
            self.tempSolution.executeRandomRemoval(sizeNBH,self.randomGen, False)
        elif destroyHeuristicNr == 2:
            self.tempSolution.executeDestroyMethod2(sizeNBH)
        else:
            self.tempSolution.executeDestroyMethod3(sizeNBH)
        
        #perform the repair
        if repairHeuristicNr == 1:
            self.tempSolution.executeRandomInsertion(self.randomGen)
        elif repairHeuristicNr == 2:
            self.tempSolution.executeRepairMethod2()
        else:
            self.tempSolution.executeRepairMethod3()


