# convenience class for interacting with tables of saved rates.
from pathlib import Path
import os
import json
import math
from anomalyDetection.paperCode.plottingUtilities.scoreMaxAndMins import scoreMaxAndMinHelper
from anomalyDetection.anomalyTriggerSkunkworks.plotSettings.utilities import convertEffToRate, convertRateToEff

class rateTableHelperBase():
    def __init__(
            self,
            jsonLocation: Path,
    ):
        self.jsonLocation = jsonLocation
        try:
            theFile = open(self.jsonLocation)
        except:
            self.rateTable = None
        else:
            self.rateTable = json.load(theFile)

    #binary search for the closest threshold to a desired rate
    def getThresholdForRate(self, score, rate):
        scoreTable = self.rateTable[score]
        scoreTableKeys = list(scoreTable.keys())
        nKeys = len(scoreTableKeys)
        
        upperBound = nKeys-1
        lowerBound = 0

        searchKey = None
        searchVal = None

        while True:
            if math.ceil((upperBound+lowerBound)/2) == searchKey: #we're searching the same spot twice, we're done
                break
            searchKey = math.ceil((upperBound+lowerBound)/2)
            searchVal = scoreTable[scoreTableKeys[searchKey]]
            
            # rate's too high, need to search a higher threshold
            if (searchVal > rate): 
                lowerBound = searchKey
            # rate's too low, need to search a lower threshold
            elif (searchVal < rate):
                upperBound = searchKey
        return scoreTableKeys[searchKey], scoreTable[scoreTableKeys[searchKey]]

    def getRateForThreshold(self, score, threshold):
        scoreTable = self.rateTable[score]
        scoreTableKeys = list(scoreTable.keys())
        nKeys = len(scoreTableKeys)

        upperBound = nKeys-1
        lowerBound = 0

        searchIndex = None
        searchVal = None
        
        while True:
            if math.ceil((upperBound+lowerBound)/2) == searchIndex: #we're searching the same spot twice, we're done
                break
            searchIndex = math.ceil((upperBound+lowerBound)/2)
            searchVal = float(scoreTableKeys[searchIndex])

            #threshold is too high, need to search a lower index
            if (searchVal > threshold):
                upperBound = searchIndex
            #threshold is too low, need to search a higher idnex
            elif (searchVal < threshold):
                lowerBound = searchIndex
        return scoreTable[scoreTableKeys[searchIndex]], float(scoreTableKeys[searchIndex])

class rateTableHelper(rateTableHelperBase):
    def __init__(
            self,
            jsonLocation: Path = Path(f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/paperCode/metadata/rateTables.json')
    ):
        super().__init__(jsonLocation)
        self.maxMinHelper = scoreMaxAndMinHelper()
    
    def makeScoreCounts(self, dataframe, score):
        scoreMax = self.maxMinHelper.maxes[score]
        scoreMin = self.maxMinHelper.mins[score]
        scoreDelta = abs(scoreMax - scoreMin)
        scoreStep = math.pow(10, math.floor(math.log10(scoreDelta / 100)))
        nSteps = math.ceil(scoreDelta/scoreStep)
        
        result = {}
        for i in range(nSteps):
            scoreThreshold = scoreMin+i*scoreStep
            result[scoreThreshold] = dataframe.Filter(f"{score} >= {scoreThreshold}").Count()
        return result

    def triggerCalculations(self, scoreCounts):
        for score in scoreCounts:
            for threshold in scoreCounts[score]:
                scoreCounts[score][threshold] = scoreCounts[score][threshold].GetValue()
        return scoreCounts

    def makeRateTable(self, scoreDict, totalCount):
        rateDict = {}
        for score in scoreDict:
            rateDict[score] = {}
            for threshold in scoreDict[score]:
                eff = scoreDict[score][threshold] / totalCount
                rate = convertEffToRate(eff)
                rateDict[score][threshold] = rate
        return rateDict

    def calculateRateTables(self, dataframe, scores):
        totalCount = dataframe.Count()
        scoreCounts = {}
        for score in scores:
            scoreCounts[score] = self.makeScoreCounts(dataframe, score)

        totalCount = totalCount.GetValue()
        scoreCounts = self.triggerCalculations(scoreCounts)
        
        rateTable = self.makeRateTable(scoreCounts, totalCount)
        self.rateTable = rateTable
        with open (self.jsonLocation, 'w+') as theFile:
            json.dump(self.rateTable, theFile, indent=4)
