from Objects.Problem import ProblemSet



if __name__ == "__main__":
    instanceList =  [
                "Ca1-3,5,100.txt",
                "Ca2-3,5,100.txt",
                "Ca3-3,5,100.txt",
                    ]
    nDestroyOps = 4
    nRepairOps = 5
    problemSet = ProblemSet(instanceList)
    problemSet.runALNS(nDestroyOps, nRepairOps, plotIntermediateSolutions=False, verbose = False)
    problemSet.plotResults()