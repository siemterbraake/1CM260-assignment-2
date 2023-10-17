from Objects.Problem import ProblemSet
import matplotlib.pyplot as plt

if __name__ == "__main__":
    baselineCost = [1841.3428780442798, 2013.774128187077, 1685.1656288966808, 1874.6091078294385, 1769.153213030219, 5788.733284616809, 5543.234238488508, 5802.884367257584, 5588.309429850857, 5319.255237848907, 11769.112085282555, 11164.186012775008, 10957.281215444844, 12203.217139415603, 11199.82894055436]
    baselineT = [1.7435487000038847, 1.5389491000096314, 1.5751547000254504, 1.7424930999986827, 1.7003817999502644, 3.478625599993393, 3.623696500028018, 3.426829500007443, 3.393680300039705, 3.3393831999856047, 6.521005499991588, 6.660739599959925, 6.823008200037293, 7.115664299984928, 7.41411050001625]
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
    nDestroyOps = 3
    nRepairOps = 4
    problemSet = ProblemSet(instanceList)
    problemSet.runALNS(nDestroyOps, nRepairOps, plotIntermediateSolutions=False, verbose = False)
    deltaC = [problemSet.costSolution[i] / baselineCost[i] for i in range(len(baselineCost))]
    deltaT = [problemSet.tSolution[i] / baselineT[i] for i in range(len(baselineT))]
    nInst = [[20]*5, [60]*5, [108]*5]
    instanceList = [instanceList[i][:-4] for i in range(len(instanceList))]
    baselineTagg = [sum(baselineT[0:5])/5, sum(baselineT[5:10])/5, sum(baselineT[10:15])/5]
    ALNSTagg = [sum(problemSet.tSolution[0:5])/5, sum(problemSet.tSolution[5:10])/5, sum(problemSet.tSolution[10:15])/5]
    nInstAgg = [20, 60, 108]

    # print the cost and time
    print("Cost: ", problemSet.costSolution)
    print("Time: ", problemSet.tSolution)

    # plot the times and instance size on a logscaled plot
    plt.figure(figsize=(6,6))
    plt.scatter(nInst, problemSet.tSolution, c='b', label='ALNS')
    plt.scatter(nInst, baselineT, c='r', label='Baseline (Random)')
    plt.plot(nInstAgg, ALNSTagg, c='b')
    plt.plot(nInstAgg, baselineTagg, c='r')
    plt.yscale('log')
    plt.xlabel('Number of locations')
    plt.ylabel('Time (s)')
    plt.legend()
    plt.savefig('Plots/time.png')
    plt.close()

    # plot the costs and instance name on a regular plot
    plt.figure(figsize=(6,6))
    plt.bar(instanceList, deltaC, color='b', label='ALNS')
    plt.xlabel('Instance')
    plt.xticks(rotation=30)
    plt.ylim(0, 1)
    plt.ylabel('Normalized Cost')
    plt.savefig('Plots/cost.png')
    plt.close()