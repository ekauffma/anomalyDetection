#  !/usr/bin/env python3
import ROOT
import argparse
import os
from anomalyDetection.paperCode.samples.paperSampleBuilder import samples
from rich.console import Console
from anomalyDetection.anomalyTriggerSkunkworks.plotSettings.utilities import convertEffToRate, convertRateToEff
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import cache
from createROCPlots import getVariableValueForBackgroundEff

console = Console()

def getVariableMins(scoreNames, backgroundFrame):
    maxRateEff = convertRateToEff(100.0)
    maxRateVariableValues = {}
    console.rule("100 kHz values")
    with console.status("Finding variable value corresponding to 100 kHz..."):
        for variableName in scoreNames:
            maxRateVariableValues[variableName] = getVariableValueForBackgroundEff(backgroundFrame, variableName, maxRateEff)
            console.log(f"[bold green]\[Done][/bold green] {variableName}")
    return maxRateVariableValues

def getVariableMaxes(scoreNames, backgroundFrame):
    console.rule("Max values")
    maxVariableValues = {}
    with console.status("Finding max variable value (min rate)..."):
        for variableName in scoreNames:
            maxVariableValues[variableName] = backgroundFrame.Max(variableName)
        for variableName in scoreNames:
            maxVariableValues[variableName] = maxVariableValues[variableName].GetValue()
    return maxVariableValues

def makeScorePlot(variableName, variableMin, variableMax, sampleName, dataframe):
    plotName = f'{sampleName}_{variableName}'
    theModel = ROOT.RDF.TH1DModel(
        plotName,
        plotName,
        100,
        variableMin,
        variableMax,
    )
    return dataframe.Histo1D(theModel, variableName)

def makeCDFHistogram(originalHistogram):
    scaleHisto = originalHistogram.Clone()
    #scaleHisto.Scale(1.0/scaleHisto.Integral())
    cdfHisto = originalHistogram.Clone()
    cdfHisto.SetNameTitle(
        originalHistogram.GetName()+"_cdf",
        originalHistogram.GetTitle()+"_cdf",
    )
    totalBins = originalHistogram.GetNbinsX()
    # remember, bin 0 is underflow,
    # bin 1 is the first bin,
    # bin #totalBins is the last bin
    # bin #totalBins+1 has the overflow
    # we want CDF bin 1 to be integral of bin 1-2 (underflow plus first)
    # up to bin # totalBin as integral 1-totalBin+1
    for i in range(1,totalBins+1):
        cdfHisto.SetBinContent(i, scaleHisto.Integral(i,totalBins))
    return cdfHisto

# Okay, the current calculation for this is too slow. So the idea is now this
# For each of the score/values we want ROCs for, we will calculate 
# At what value of this we an efficiency that is equivalent to 100 kHz
# Then, we will split the range from there to max into 100 bins, and make a plot of the variable
# We will then normalize it, and make CDFs out of it via integration.
# From there, we can simply match bins to come up with the graphs we want
# it may be a bit sparse towards low frequencies, but w/e, this is the price we pay
def main(args):
    #Start by getting all the samples, and weeding out Zero Bias
    mcSampleNames = list(samples.keys())
    try:
        mcSampleNames.remove('ZeroBias')
    except ValueError:
        console.log("Failed to find ZeroBias in list of samples and prune it out. Check the samples.", style="red")
        exit(1)
    zeroBiasDataframe = samples['ZeroBias'].getNewDataframe()
    # Calculate HT on data
    HTFunction = """
    try {
       for(int i = 0; i < L1Upgrade.sumType.size(); ++i){
          if(L1Upgrade.sumType.at(i) == 1 and L1Upgrade.sumBx.at(i) == 0){
             return (double) L1Upgrade.sumEt.at(i);
          }
       }
       return 0.0;
    }
    catch (const std::runtime_error& e) {
       return 0.0;
    }
    """
    zeroBiasDataframe = zeroBiasDataframe.Define(
        "HT",
        HTFunction,
    )
    # make train versus test data
    evenLumiZBDataframe = zeroBiasDataframe.Filter("lumi % 2 == 0")
    oddLumiZBDataframe = zeroBiasDataframe.Filter("lumi % 2 == 1")
    # Make list of variables/values we want to make ROC curves for
    scoreNames = [
        'CICADA_v1p2p0_score',
        'CICADA_v2p2p0_score',
        'CICADA_v1p2p0N_score',
        'CICADA_v2p2p0N_score',
        "HT"
    ]
    # Let's find the value of each variable that corresponds to a 100 kHz efficiency
    # i.e. variable minimum
    variableMins = getVariableMins(scoreNames, oddLumiZBDataframe)
    #debug:
    # variableMins = {}
    # for scoreName in scoreNames:
    #     variableMins[scoreName] = 0.0

    # let's find the max of each of these variables
    #variableMaxes = getVariableMaxes(scoreNames, oddLumiZBDataframe)
    console.rule("Max values")
    variableMaxes = {}
    for scoreName in scoreNames:
        if scoreName != 'HT':
            variableMaxes[scoreName] = 256.0
        else:
            variableMaxes[scoreName] = 400.0
    console.log("Done!")

    console.rule("Values")
    console.print(variableMins)
    console.print(variableMaxes)

    # then for each score and each sample + data, make 100 bin histograms
    console.rule("Making base score plots")
    allPlots = []
    for variableName in scoreNames:
        console.log(variableName)
        console.log("\tTrain_ZeroBias")
        trainZeroBiasName = f"Train_ZeroBias_{variableName}"
        trainZeroBiasModel = ROOT.RDF.TH1DModel(
            trainZeroBiasName,
            trainZeroBiasName,
            100,
            variableMins[variableName],
            variableMaxes[variableName]
        )
        trainZeroBiasPlot = evenLumiZBDataframe.Histo1D(trainZeroBiasModel, variableName)
        trainZeroBiasEvents = evenLumiZBDataframe.Count().GetValue()
        trainZeroBiasPlot.Scale(1.0/trainZeroBiasEvents)

        console.log("\tTest_ZeroBias")
        testZeroBiasName = f"Test_ZeroBias_{variableName}"
        testZeroBiasModel = ROOT.RDF.TH1DModel(
            testZeroBiasName,
            testZeroBiasName,
            100,
            variableMins[variableName],
            variableMaxes[variableName],
        )
        testZeroBiasPlot = oddLumiZBDataframe.Histo1D(testZeroBiasModel, variableName)
        testZeroBiasEvents = oddLumiZBDataframe.Count().GetValue()
        testZeroBiasPlot.Scale(1.0/testZeroBiasEvents)
        
        allPlots.append(trainZeroBiasPlot.GetValue())
        allPlots.append(testZeroBiasPlot.GetValue())
        
    for sampleName in mcSampleNames:
        console.log(f'{sampleName}')
        sampleDF = samples[sampleName].getNewDataframe()
        sampleDF = sampleDF.Define(
            "HT",
            HTFunction,
        )
        sampleEvents = sampleDF.Count().GetValue()
        for variableName in scoreNames:
            console.log(f'\t{variableName}')
            plotName = f'{sampleName}_{variableName}'
            theModel = ROOT.RDF.TH1DModel(
                plotName,
                plotName,
                100,
                variableMins[variableName],
                variableMaxes[variableName],
            )
            thePlot = sampleDF.Histo1D(theModel, variableName).GetValue()
            thePlot.Scale(1.0/sampleEvents)
            allPlots.append(
                thePlot
            )
    console.log("Done!")

    # Then we can make CDFs for each of these histograms 
    # We don't even really have to do this here I guess...
    console.rule("CDFs")
    cdfHistos = [makeCDFHistogram(x) for x in allPlots]
    console.log("Done!")

    console.rule("Output")
    # make an output area
    plotOutputLocation = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles'
    os.makedirs(plotOutputLocation, exist_ok=True)
    outputFileName = os.path.join(plotOutputLocation, 'fastROCCurves.root')
    theOutputFile = ROOT.TFile(outputFileName, 'RECREATE')
    for plot in cdfHistos:
        plot.Write()
    for plot in allPlots:
        plot.Write()
    # Save everything to file
    theOutputFile.Write()
    theOutputFile.Close()
    console.log("Done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run faster calculation of ROC')

    args = parser.parse_args()

    main(args)
