from anomalyDetection.paperCode.plottingUtilities.scoreMaxAndMins import scoreMaxAndMinHelper
from anomalyDetection.paperCode.plottingUtilities.rateTables import rateTableHelper
from anomalyDetection.paperCode.plottingUtilities.unprescaledTriggerHelper import unprescaledTriggerHelper
from anomalyDetection.paperCode.plottingUtilities.pureRateTables import pureRateTableHelper

from anomalyDetection.paperCode.samples.paperSampleBuilder import reducedSamples as samples
from anomalyDetection.paperCode.plottingUtilities.models import standardScoreGroups, getAllScoreNames

from rich.console import Console

console = Console()

def makeAllScoreNamesFromGroups(listOfGroups):
    scoreNameList = []
    for group in listOfGroups:
        scoreNameList.append(group.adjustedTeacherScoreName)
        for studentModelName in group.studentModels:
            scoreNameList.append(group.studentModels[studentModelName].scoreName)
    return scoreNameList

def main():
    cicadaScoreGroups = standardScoreGroups
        
    allDFs = {}
    for sampleName in samples:
        allDFs[sampleName] = samples[sampleName].getNewDataframe()
        for group in cicadaScoreGroups:
            allDFs[sampleName] = group.applyFrameDefinitions(allDFs[sampleName])
    scoreNames = getAllScoreNames(cicadaScoreGroups)
    
    console.log('Max and min calculation')
    theMinMaxHelper = scoreMaxAndMinHelper()
    theMinMaxHelper.calculateScoreMaxesAndMins(scoreNames, allDFs)
    console.log("Done!")

    console.log('Rate tables')
    theRateTableHelper = rateTableHelper()
    theRateTableHelper.calculateRateTables(allDFs["ZeroBias"], scoreNames)
    console.log("Done!")

    console.log('Unprescaled trigger calculation')
    theUnprescaledTriggerHelper = unprescaledTriggerHelper()
    theUnprescaledTriggerHelper.calculateListOfUnprescaledTriggers(allDFs['ZeroBias'])
    console.log('Done!')

    console.log('Pure rate tables')
    thePureRateTableHelper = pureRateTableHelper()
    thePureRateTableHelper.calculatePureRateTables(allDFs["ZeroBias"], scoreNames)
    console.log('Done!')

if __name__ == '__main__':
    main()
