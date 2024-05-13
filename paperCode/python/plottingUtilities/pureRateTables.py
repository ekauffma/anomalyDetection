from pathlib import Path
import os
import json
from anomalyDetection.paperCode.plottingUtilities.unprescaledTriggerHelper import unprescaledTriggerHelper
from anomalyDetection.paperCode.plottingUtilities.rateTables import rateTableHelper, rateTableHelperBase

class pureRateTableHelper(rateTableHelperBase):
    def __init__(
            self,
            jsonLocation: Path = Path(f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/paperCode/metadata/pureRateTables.json')
    ):
        super().__init__(jsonLocation)
        self.theRateTableHelper = rateTableHelper()
        self.theUnprescaledTriggerHelper = unprescaledTriggerHelper()

    def calculatePureRateTables(self, dataframe, scores):
        pureRateTable = {}
        totalEvents = {}
        pureEvents = {}
        # for each score
        for score in scores:
            totalEvents[score] = {}
            pureEvents[score] = {}
            #and for each threshold in the rate table for that score
            for threshold in self.theRateTableHelper.rateTable[score]:
                # we book a calculation of total number of events in the dataframe above that score
                totalEvents[score][threshold] = dataframe.Filter(f'{score} >= {threshold}').Count()
                # and total number of pure events above that threshold

                pureEvents[score][threshold] = dataframe.Filter(f'{score} >= {threshold}').Filter(self.theUnprescaledTriggerHelper.getNoOverlapString()).Count()
                
        #Now we trigger all calculations
        for score in totalEvents:
            for threshold in totalEvents[score]:
                totalEvents[score][threshold] = totalEvents[score][threshold].GetValue()
                pureEvents[score][threshold] = pureEvents[score][threshold].GetValue()
        #then again for each score and threshold
        for score in totalEvents:
            pureRateTable[score] = {}
            for threshold in totalEvents[score]:
                # we apply that pure fraction to the rate table to get a pure rate
                try:
                    pureFraction = pureEvents[score][threshold]/totalEvents[score][threshold]
                except ZeroDivisionError:
                    pureFraction = 0.0
                #then we put that in the pure rate table
                pureRateTable[score][threshold] = pureFraction * self.theRateTableHelper.rateTable[score][threshold]

        self.rateTable = pureRateTable

        with open(self.jsonLocation, 'w+') as theFile:
            json.dump(
                self.rateTable,
                theFile,
                indent=4,
            )
