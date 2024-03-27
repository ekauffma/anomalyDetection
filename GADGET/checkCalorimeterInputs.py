import h5py
import numpy as np
import scipy
import matplotlib.pyplot as plt
from rich.console import Console
from scipy.optimize import curve_fit
from pathlib import Path

console = Console()

def powerLaw(x, *p):
    alpha, n = p
    return alpha/np.power(x+1, n)

def inverseLog(x, *p):
    alpha, n = p
    return alpha/np.power(np.log(x+2), n)

def testFun(x, *p):
    alpha, n, c = p
    return alpha*np.power(np.log(x+c), n)

def makeInputRegionPlusFits(allRegionEnergies, outputDir, nBins=50):
    amounts, binEdges, _ = plt.hist(
        allRegionEnergies,
        bins=nBins,
        alpha=0.6,
        label="Region Energies",
    )
    plt.xlabel("Region energy")
    plt.ylabel("Instances")
    plt.yscale("log")
    
    binCenters = (binEdges[:-1]+binEdges[1:])/2
    alphaGuess = np.max(amounts)
    nGuess = -2.0
    cGuess = 0.0
    
    testFunParams = [alphaGuess, nGuess, cGuess]
    testFunCoeff, testFunMatrix = curve_fit(testFun, binCenters, amounts, p0=testFunParams, maxfev=100000)
    console.print(f"Fit alpha: {testFunCoeff[0]}")
    console.print(f"Fit n: {testFunCoeff[1]}")
    console.print(f"Fit c: {testFunCoeff[2]}")
    fit_x = np.linspace(min(allRegionEnergies), max(allRegionEnergies), nBins)
    plt.plot(fit_x, testFun(fit_x, *testFunCoeff), 'r-', label="Test Function Fit")

    plt.savefig(f"{outputDir}/input_distribution.png")

    plt.close()

def main():
    with h5py.File("/hdfs/store/user/aloelige/CICADA_Training/22Jan2024/ZeroBias_EvenLumi.h5") as theFile:
        theDataset = np.array(theFile["CaloRegions"])

    plotOutputDir = Path("plots")
    plotOutputDir.mkdir(parents=True, exist_ok=True)

    console.print(theDataset.shape)
    allRegionEnergies = theDataset.reshape(-1,)
    makeInputRegionPlusFits(allRegionEnergies, plotOutputDir)
    

if __name__ == '__main__':
    main()
