from anomalyDetection.paperCode.plottingUtilities.scoreMaxAndMins import scoreMaxAndMinHelper
from anomalyDetection.paperCode.samples.paperSampleBuilder import reducedSamples as samples
from anomalyDetection.paperCode.plottingUtilities.models import *
from anomalyDetection.anomalyTriggerSkunkworks.plotSettings.utilities import convertEffToRate, convertRateToEff

from rich.table import Table
from rich.console import Console
import math

import json
from pathlib import Path
import os

console = Console()

def makeAllScoreNamesFromGroups(listOfGroups):
    scoreNameList = []
    for group in listOfGroups:
        scoreNameList.append(group.adjustedTeacherScoreName)
        for studentModelName in group.studentModels:
            scoreNameList.append(group.studentModels[studentModelName].scoreName)
    return scoreNameList

def weedOutBadValues(theList):
    for score in theList:
        if math.isinf(theList[score]):
            console.print("Found infinte value in min/max list. Setting it to 0.0")
            theList[index] = 0.0

def makeScoreCounts(zeroBiasDF, scoreName, scoreMax, scoreMin):
    console.log(f"Making rates for score: {scoreName}")
    console.log(f"Max: {scoreMax}, scoreMin: {scoreMin}")
    scoreDelta = scoreMax - scoreMin
    scoreStep = math.pow(10, math.floor(math.log10(scoreDelta // 100)))
    nSteps = math.ceil(scoreDelta/scoreStep)
    console.log(f"Will use steps of size: {scoreStep}, for a total of {nSteps}")
    console.print()
    
    result = {}
    for i in range(nSteps):
        scoreThreshold = scoreMin+i*scoreStep
        result[scoreThreshold]=zeroBiasDF.Filter(f'{scoreName} >= {scoreThreshold}').Count()
    return result

def triggerCalculations(scoreCounts):
    for score in scoreCounts:
        for threshold in scoreCounts[score]:
            scoreCounts[score][threshold] = scoreCounts[score][threshold].GetValue()
    return scoreCounts

def makeRateDict(scoreDict, totalCounts):
    rateDict = {}
    for score in scoreDict:
        rateDict[score] = {}
        for threshold in scoreDict[score]:
            eff = scoreDict[score][threshold] / totalCounts
            rate = convertEffToRate(eff)
            rateDict[score][threshold] = rate
    return rateDict

def dumpRateTable(rateTable):
    for score in rateTable:
        table=Table(title=score)
        table.add_column('Threshold', justify='left')
        table.add_column('Rate (kHz)', justify='right')
        
        for threshold in rateTable[score]:
            table.add_row(f'{threshold}', f'{rateTable[score][threshold]}')
        console.print(table)

def main():
    theMinMaxHelper = scoreMaxAndMinHelper()
    cicadaScoreGroups = [
        CICADA_vXp2p0_Group,
        CICADA_vXp2p0N_Group,
        CICADA_vXp2p1_Group,
        CICADA_vXp2p1N_Group,
        CICADA_vXp2p2_Group,
        CICADA_vXp2p2N_Group,
    ]
        
    allDFs = {}
    for sampleName in samples:
        allDFs[sampleName] = samples[sampleName].getNewDataframe()
        for group in cicadaScoreGroups:
            allDFs[sampleName] = group.applyFrameDefinitions(allDFs[sampleName])
    scoreNames = makeAllScoreNamesFromGroups(cicadaScoreGroups)
    scoreNames.append('CICADA_v2p1p2')
    
    console.rule('Max and min calculation')
    console.log("Trigger calculation")
    scoreMaxes, scoreMins = theMinMaxHelper.getScoreMaxesAndMins(scoreNames, allDFs)
    console.log("Finished")
    weedOutBadValues(scoreMaxes)
    weedOutBadValues(scoreMins)
    console.print(scoreMaxes)
    console.print(scoreMins)

    console.rule('Rate tables')

    totalCount = allDFs['ZeroBias'].Count()
    scoreCounts = {}
    for score in scoreNames:
        console.log(score)
        scoreCounts[score] = makeScoreCounts(allDFs['ZeroBias'], score, scoreMaxes[score], scoreMins[score])

    console.print()
    console.log('Triggering calculation')
    totalCount = totalCount.GetValue()
    scoreCounts = triggerCalculations(scoreCounts)

    rateDict = makeRateDict(scoreCounts, totalCount)
    dumpRateTable(rateDict)

    jsonOutputPath = Path(f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/paperCode/metadata/rateTables.json')
    with open(jsonOutputPath, 'w+') as theFile:
        json.dump(rateDict, theFile, indent=4)
    console.log("Done!")

if __name__ == '__main__':
    main()
