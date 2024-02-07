# !/usr/bin/env python3
import ROOT
import argparse
import os
from anomalyDetection.paperCode.samples.paperSampleBuilder import samples
from rich.console import Console
from anomalyDetection.anomalyTriggerSkunkworks.plotSettings.utilities import convertEffToRate, convertRateToEff

console = Console()

def getSampleEffForValue(sample, variable, value):
    totalSampleCount = sample.Count()
    thresholdFrame = sample.Filter(f'{variable} >= {value}')
    thresholdCount = thresholdFrame.Count()

    eff = thresholdCount.GetValue() / totalSampleCount.GetValue()

    return eff

def getVariableValueForBackgroundEff(background, variable, efficiencyWorkingPoint, iterations=100, epsilonPercent = 1e-2):
    testValue = 0.0
    testEff = 1.0

    variableLowerBound = 0.0
    if variable == 'HT':
        variableUpperBound = 5000.0
    else:
        variableUpperBound = 256.0

    for i in range(iterations):
        if abs(testEff-efficiencyWorkingPoint) < epsilonPercent*efficiencyWorkingPoint:
            break
        
        # if the test eff is less than the required eff, then we have cut too high, and need to relax the cut
        if testEff < efficiencyWorkingPoint:
            variableUpperBound = testValue
            testValue = (variableLowerBound+testValue)/2
        # otherwise if the test eff is higher than the required eff, then we have cut too low and need to tighten the cut
        else:
            variableLowerBound = testValue
            testValue = (variableUpperBound+testValue) / 2
        #now our new test efficiency becomes whatever the efficiency on this sample at the test value
        testEff = getSampleEffForValue(background, variable, testValue)
    return testValue
    
def makeROCCurveFromPoints(points, nameTitle):
    nPoints = len(points)
    rocGraph = ROOT.TGraph(nPoints)
    for i, point in enumerate(points):
        rocGraph.SetPoint(i, point[0], point[1])
    rocGraph.SetNameTitle(
        nameTitle,
        nameTitle,
    )
    return rocGraph

# given a sample, make a ROC curve from it
# Let's start by just with 100 efficiency points between rate 0, and 100 kHz
def makeROCCurveForVariable(signal, background, sampleName, variable):
    desiredRates = [ i*1.0 for i in range(101) ]
    desiredEffs = [ convertRateToEff(x) for x in desiredRates ]

    effPoints = []
    for efficiencyWorkingPoint in desiredEffs:
        # okay, let's figure out what value of the variable gets us the desired eff in the background sample
        variableValue = getVariableValueForBackgroundEff(background, variable, efficiencyWorkingPoint)
        signalEff = getSampleEffForValue(signal, variable, variableValue)

        effPoints.append((efficiencyWorkingPoint, signalEff))
    #okay, now we can build a graph with the working points 
    nameTitle = f'{sampleName}_{variable}'
    rocGraph = makeROCCurveFromPoints(effPoints, nameTitle)
    return rocGraph

def main(args):
    mcSampleNames = list(samples.keys())
    try:
        mcSampleNames.remove('ZeroBias')
    except ValueError:
        console.log("Failed to find ZeroBias in list of samples and prune it out. Check the samples.", style="red")
        exit(1)

    #Now let's create the even/odd train/test dataframes
    zeroBiasDataframe = samples['ZeroBias'].getNewDataframe()
    #very quickly, let's go ahead and define the HT column for zero bias
    HTFunction = """
    for(int i = 0; i < sumType.size(); ++i){
       if(sumType.at(i) == 1){
          return (double) sumEt.at(i);
       }
    }
    return 0.0;
    """
    zeroBiasDataframe = zeroBiasDataframe.Define(
        "HT",
        HTFunction,
    )

    evenLumiZBDataframe = zeroBiasDataframe.Filter("lumi % 2 == 0")
    oddLumiZBDataframe = zeroBiasDataframe.Filter("lumi % 2 == 1")

    scoreNames = [
        'CICADA_v1p2p0_score',
        'CICADA_v2p2p0_score',
        'CICADA_v1p2p0N_score',
        'CICADA_v2p2p0N_score',
        "HT"
    ]
    allPlots = []
    mcDataframes = []

    #now we go over each MC frame, and make a ROC curve with HT on it for it
    with console.status("Making ROCs..."):
        for sampleName in mcSampleNames:
            theDataframe = samples[sampleName].getNewDataframe()
            theDataframe = theDataframe.Define(
                "HT",
                HTFunction,
            )
            
            # now for this plot we need to make 5 ROC plots. One for each of the scores
            # and HT
            #Let's offload this problem
            for variable in scoreNames:
                allPlots += makeROCCurveForVariable(
                    theDataframe,
                    oddLumiZBDataframe,
                    sampleName,
                    variable,
                )
            
            console.log(f"[bold green]\[Done][/bold green]: {sampleName}")

    plotOutputLocation = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/'
    os.makedirs(plotOutputLocation, exist_ok=True)
    outputFileName = os.path.join(plotOutputLocation, 'rocCurves.root')
    theOutputFile = ROOT.TFile(outputFileName, 'RECREATE')
    with console.status('Writing plot file...'):
        for plot in allPlots:
            plot.Write()
        theOutputFile.Write()
        theOutputFile.Close()
    console.log(f'[bold green]\[Done][/bold green] Writing files')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create ROC plots from the paper samples")
    
    args = parser.parse_args()
    main(args)
