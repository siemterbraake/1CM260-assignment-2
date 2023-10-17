from Objects.Problem import ProblemSet

if __name__ == "__main__":
    baselineCost = [1700.7059682222073, 
                       2084.8087319244783, 
                       1583.757764322537, 
                       1885.1711044781907, 
                       1777.6051093947885, 
                       5329.268883590882, 
                       5451.372192309404, 
                       5669.712850247063, 
                       5118.507635595703, 
                       5255.10777494041, 
                       10474.239826597142, 
                       9953.743018893138, 
                       9732.728888788635, 
                       10876.936432963526, 
                       9970.33747823218]   
    baselineT = [2.7229589000344276, 
                 1.9903085000114515, 
                 2.7795700000133365, 
                 2.19861259998288, 
                 2.0499106000061147, 
                 14.019081000005826, 
                 12.161108399974182, 
                 11.452378100017086, 
                 12.28826120001031, 
                 8.166467599978205, 
                 61.28554929996608, 
                 58.32274930004496, 
                 63.95776340004522, 
                 56.197587899980135, 
                 63.218860199966]
    instanceList =  [
                "Ca1-2,3,15.txt",
                "Ca2-2,3,15.txt",
                "Ca3-2,3,15.txt",
                "Ca4-2,3,15.txt",
                "Ca5-2,3,15.txt",
                "Ca1-6,4,50.txt",
                "Ca2-6,4,50.txt",
                "Ca3-6,4,50.txt",
                "Ca4-6,4,50.txt",
                "Ca5-6,4,50.txt",
                "Ca1-3,5,100.txt",
                "Ca2-3,5,100.txt",
                "Ca3-3,5,100.txt",
                "Ca4-3,5,100.txt",
                "Ca5-3,5,100.txt",
                    ]
    nDestroyOps = 4
    nRepairOps = 3
    problemSet = ProblemSet(instanceList)
    problemSet.runALNS(nDestroyOps, nRepairOps, plotIntermediateSolutions=False, verbose = False)
    deltaC = [problemSet.costSolution[i] / baselineCost[i] for i in range(len(baselineCost))]
    deltaT = [problemSet.tSolution[i] / baselineT[i] for i in range(len(baselineT))]
    meanDC = sum(deltaC)/len(deltaC)
    meanDT = sum(deltaT)/len(deltaT)
    print("Mean delta cost: ", meanDC)
    print("Mean delta time: ", meanDT)