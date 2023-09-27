# -*- coding: utf-8 -*-
"""
@author: Original template by Rolf van Lieshout and Krissada Tundulyasaree
"""

from Problem import TWO_E_CVRP
from ALNS import ALNS

testI = "Ca1-2,3,50.txt"
dir = "Optional"
problem = TWO_E_CVRP.readInstance(testI, dir)
nDestroyOps = 1
nRepairOps = 1
alns = ALNS(problem, nDestroyOps, nRepairOps)
alns.execute()
print(alns.bestSolution)
