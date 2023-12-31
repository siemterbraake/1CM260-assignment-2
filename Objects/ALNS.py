# -*- coding: utf-8 -*-
"""
@author: Original template by Rolf van Lieshout and Krissada Tundulyasaree
"""
import matplotlib.pyplot as plt
from Objects.Solution import Solution
from random import Random
import copy
import time
import math


class Parameters:
    """
    Class that holds all the parameters for ALNS
    """
    nIterations = 500  # number of iterations of the ALNS
    minSizeNBH = 1  # minimum neighborhood size
    randomSeed = 1  # value of the random seed
    T = 100 # Temperature for Simulated Annealing
    Cool = 0.99 # Cooling rate
    # can add parameters such as cooling rate etc.


class ALNS:
    """
    Class that models the ALNS algorithm. 

    Parameters
    ----------
    problem : The problem instance that we want to solve.
    timeReg: time regularization option
    nDestroyOps : number of destroy operators.
    nRepairOps :  number of repair operators.
    wDestroyOps : weight of destroy operator.
    wRepairOps : weight of repair operator.
    randomGen :  random number generator
    currentSolution : The current solution in the ALNS algorithm
    bestSolution : The best solution currently found
    bestCost : Cost of the best solution

    """
    def __init__(self,problem, nDestroyOps: int, nRepairOps: int, verbose: bool = False):
        self.problem = problem
        self.nDestroyOps = nDestroyOps
        self.nRepairOps = nRepairOps
        self.verbose = verbose
        self.wDestroyOps = [1]*nDestroyOps #initially all destroy operators have weight 1
        self.tDestroyOps = [0]*nDestroyOps #initially all destroy operators have time 0
        self.nUsedDestroyOps = [0]*nDestroyOps #initially all destroy operators are used 0 times
        self.wRepairOps = [1]*nRepairOps #initially all repair operators have weight 1
        self.tRepairOps = [0]*nRepairOps #initially all repair operators have time 0
        self.nUsedRepairOps = [0]*nRepairOps #initially all destroy operators are used 0 times
        self.wLambda = 0.5 #parameter that controls the sensitivity of the weights
        self.randomGen = Random(Parameters.randomSeed) #used for reproducibility
        self.solutionTrend = list() #list that stores the best solution found at each iteration
        self.currentSolutionTrend = list() #list that stores the current solution found at each iteration
        self.bestSolutionTrend = list() #list that stores the best solution found at each iteration
        self.wRepairOpsTrend = [list() for _ in range(nRepairOps)] #list that stores the weights of the repair operators at each iteration
        
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
        self.solutionTrend.append(self.bestCost)
        if self.verbose:
            print("Created initial solution with cost: "+str(self.bestCost))
        
    def execute(self, plotIntermediateSolutions: bool = False):
        """
        Method that executes the ALNS
        """
        starttime = time.time() # get the start time
        self.constructInitialSolution()
        
        for i in range(Parameters.nIterations):
            #copy the current solution
            self.tempSolution = copy.deepcopy(self.currentSolution)
            #decide on the size of the neighbourhood
            sizeNBH = self.randomGen.randint(Parameters.minSizeNBH,len(self.problem.locations)//2)
            #decide on the destroy and repair operator numbers
            destroyOpNr = self.determineDestroyOpNr()
            repairOpNr = self.determineRepairOpNr()
            #execute the destroy and the repair and evaluate the result
            self.destroyAndRepair(destroyOpNr, repairOpNr, sizeNBH)
            # Determine the first echelon route using the Greedy insertion
            self.tempSolution.computeCost()
            if self.verbose:
                print(f"Iteration {i}: Found solution with cost: {self.tempSolution.cost}")
            #determine if the new solution is accepted
            score = self.checkIfAcceptNewSol(i, destroyOpNr, repairOpNr, plotIntermediateSolutions)
            #update the ALNS weights
            self.updateWeights(destroyOpNr, repairOpNr, score)
            #update the time and number of uses of the operators
            self.nUsedDestroyOps[destroyOpNr-1] += 1
            self.nUsedRepairOps[repairOpNr-1] += 1
            #store the best solution found at each iteration
            self.solutionTrend.append(self.tempSolution.cost)
            self.currentSolutionTrend.append(self.currentSolution.cost)
            self.bestSolutionTrend.append(self.bestSolution.cost)

            if self.verbose:
                if self.tempSolution.cost > 1.75*self.bestSolution.cost:
                    print(f"Very bad solution found. Destory operator: {destroyOpNr}, repair operator: {repairOpNr}")
                    if plotIntermediateSolutions:
                        self.tempSolution.plotRoutes(f"ALNS Iteration {i}")              

        endtime = time.time() # get the end time
        cpuTime = round(endtime-starttime)
        self.plotSolutionTrend()
        self.PlotRepairTrend()
        self.bestSolution.plotRoutes("ALNS Best Solution")

        print("Terminated. Final cost: "+str(self.bestSolution.cost)+", cpuTime: "+str(cpuTime)+" seconds")
        print(f"Time for the destroy operators: {self.tDestroyOps}. Weights for the destroy operators: {self.wDestroyOps}")

        print(f"Time for the repair operators: {self.tRepairOps}. Weights for the repair operators: {self.wRepairOps}")
    
    def checkIfAcceptNewSol(self, i: int, destroyOpNr: int, repairOpNr: int, plotIntermediateSolutions: bool = False):
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
            if self.verbose:
                print(f"Found new global best solution using destroy operator {destroyOpNr} and repair operator {repairOpNr}")
            score = 2
            Parameters.T = Parameters.Cool*Parameters.T

            if plotIntermediateSolutions:
                self.tempSolution.plotRoutes(f"ALNS Iteration {i}")
            return score
        
        else:
            diff = self.tempSolution.cost - self.currentSolution.cost
            prob = math.exp(-diff/Parameters.T)
            p = self.randomGen.random()
            Parameters.T = Parameters.Cool*Parameters.T
            if p < prob:
                self.currentSolution = copy.deepcopy(self.tempSolution)
                score = 1
                return score
            else:
                score = 0
                return score
            
    def updateWeights(self, destroyOpNr: int, repairOpNr: int, score: int, decay: float = 0.99):
        """
        Method that updates the weights of the destroy and repair operators
        """
        self.wDestroyOps[destroyOpNr-1] = (1-self.wLambda)*self.wDestroyOps[destroyOpNr-1] + self.wLambda*score
        self.wRepairOps[repairOpNr-1] =  (1-self.wLambda)*self.wRepairOps[repairOpNr-1] + self.wLambda*score
        self.wLambda = self.wLambda*decay #update the lambda parameter

        self.wDestroyOps = [i/sum(self.wDestroyOps) for i in self.wDestroyOps] #normalize the weights
        self.wRepairOps = [i/sum(self.wRepairOps) for i in self.wRepairOps] #normalize the weights

        for i in range(self.nRepairOps):
            self.wRepairOpsTrend[i].append(self.wRepairOps[i])

    
    def determineDestroyOpNr(self) -> int:
        """
        Method that determines the destroy operator that will be applied. 
        Currently we just pick a random one with equal probabilities. 
        Could be extended with weights
        """
        # if NOT all operators have been used at least once, we use the regular weights
        if 0 in self.nUsedDestroyOps:
             return self.randomGen.choices(range(1,self.nDestroyOps+1),weights=self.wDestroyOps,k=1)[0]
        
        # if all operators have been used at least once, we use the weights based on the average time
        else:
            timeWeights = [self.wDestroyOps[i]/self.tDestroyOps[i] for i in range(self.nDestroyOps)]
            return self.randomGen.choices(range(1,self.nDestroyOps+1),weights=timeWeights,k=1)[0]

    def determineRepairOpNr(self) -> int:
        """
        Method that determines the repair operator that will be applied. 
        Currently we just pick a random one with equal probabilities. 
        Could be extended with weights
        """
        if 0 in self.nUsedRepairOps:
            return self.randomGen.choices(range(1,self.nRepairOps+1),weights=self.wRepairOps,k=1)[0]
        
        # if all operators have been used at least once, we use the weights based on the average time
        else:
            timeWeights = [self.wRepairOps[i]/self.tRepairOps[i] for i in range(self.nRepairOps)]
            return self.randomGen.choices(range(1,self.nRepairOps+1),weights=timeWeights,k=1)[0]
    
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
        startTime_destroy = time.perf_counter() # precision timing
        if destroyHeuristicNr == 1:
            self.tempSolution.executeRandomRemoval(sizeNBH,self.randomGen, False)
        elif destroyHeuristicNr == 2:
            self.tempSolution.executeWorstRemoval(sizeNBH,self.randomGen, False, False)
        elif destroyHeuristicNr == 3:
            self.tempSolution.executeWorstRemoval(sizeNBH, self.randomGen, False, True)
        else: # SHOWS POOR PERFORMANCE, NOT USED
            self.tempSolution.executeRelatedRemoval(sizeNBH,self.randomGen, False)
        tDestroy = time.perf_counter()-startTime_destroy

        #perform the repair
        startTime_repair = time.perf_counter() # precision timing
        if repairHeuristicNr == 1:
            self.tempSolution.executeRandomInsertion(self.randomGen)
        elif repairHeuristicNr == 2:
            self.tempSolution.executeGreedyInsertion(self.randomGen, True)
        elif repairHeuristicNr == 3:
            self.tempSolution.executeRegretInsertion(self.randomGen, True)
        elif repairHeuristicNr == 4: # SHOWS POOR PERFORMANCE, NOT USED
            self.tempSolution.executeRegretInsertion(self.randomGen, False)
        else: # SHOWS POOR PERFORMANCE, NOT USED
            self.tempSolution.executeGreedyInsertion(self.randomGen, False)
            
        tRepair = time.perf_counter()-startTime_repair

        #store average perform times (iterative expression)
        if self.nUsedDestroyOps[destroyHeuristicNr-1] == 0:
            self.tDestroyOps[destroyHeuristicNr-1] = tDestroy
            self.tRepairOps[repairHeuristicNr-1] = tRepair
        else:
            self.tDestroyOps[destroyHeuristicNr-1] = (self.nUsedDestroyOps[destroyHeuristicNr-1]*self.tDestroyOps[destroyHeuristicNr-1] + tDestroy)/(self.nUsedDestroyOps[destroyHeuristicNr-1]+1)
            self.tRepairOps[repairHeuristicNr-1] = (self.nUsedRepairOps[repairHeuristicNr-1]*self.tRepairOps[repairHeuristicNr-1] + tRepair)/(self.nUsedRepairOps[repairHeuristicNr-1]+1)

    def plotSolutionTrend(self):
        """
        Method that plots the solution trend
        """
        plt.figure(figsize=(4,3))
        plt.plot(self.currentSolutionTrend, label='Current Solution')
        plt.plot(self.bestSolutionTrend, label='Best Solution')
        plt.ylabel('Cost')
        plt.xlabel('Iteration')
        plt.legend()
        plt.tight_layout()
        plt.savefig('Plots/ALNS.png')
        plt.close()

    def PlotRepairTrend(self):
        """
        Method that plots the repair weight trend
        """
        plt.figure(figsize=(4,3))
        for i in range(self.nRepairOps):
            plt.plot(self.wRepairOpsTrend[i], label=f'Repair Operator {i+1}')
        plt.ylabel('Weight')
        plt.xlabel('Iteration')
        plt.legend(loc="upper right", prop = { "size": 8})
        plt.tight_layout()
        plt.savefig('Plots/RepairOps.png')
        plt.close()

