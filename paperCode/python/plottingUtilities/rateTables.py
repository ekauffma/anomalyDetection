# convenience class for interacting with tables of saved rates.
from pathlib import Path
import os
import json
import math

class rateTableHelper():
    def __init__(
            self,
            jsonLocation: Path = Path(f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/paperCode/metadata/rateTables.json')
    ):
        self.jsonLocation = jsonLocation
        with open(self.jsonLocation) as theFile:
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
