# -*- coding: utf-8 -*-
"""
@author: Original template by Rolf van Lieshout and Krissada Tundulyasaree
"""

from Problem import ProblemSet
from Setup import instanceList

if __name__ == "__main__":
    nDestroyOps = 4
    nRepairOps = 5
    problemSet = ProblemSet(instanceList)
    problemSet.runALNS(nDestroyOps, nRepairOps)