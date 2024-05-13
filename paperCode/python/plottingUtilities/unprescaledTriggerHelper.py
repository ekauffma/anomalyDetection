# convenience class for calculating, storing, and accessing unprescaled triggers in a sample
from pathlib import Path
import os
import json

class unprescaledTriggerHelper():
    def __init__(
            self,
            jsonLocation: Path = Path(f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/paperCode/metadata/unprescaledTriggerTables.json')
    ):
        self.jsonLocation = jsonLocation
        try:
            theFile = open(self.jsonLocation)
        except:
            self.triggerTables = None
        else:
            self.triggerTables = json.load(theFile)

    def getListOfTriggers(self, dataframe):
        listOfColumns = dataframe.GetColumnNames()
        listOfTriggers = [str(x) for x in listOfColumns if ('L1_' in str(x) and '_prescale' not in str(x))]
        listOfTriggers = [x.split('.')[1] for x in listOfTriggers]
        return listOfTriggers

    def calculateListOfUnprescaledTriggers(self, dataframe):
        listOfTriggers = self.getListOfTriggers(dataframe)
        counts = {}
        unprescaledTriggers, prescaledTriggers = [], []

        for trigger in listOfTriggers:
            prescaleColumn = f'{trigger}_prescale'
            counts[trigger] = dataframe.Filter(f'{prescaleColumn} != 1').Count()
            
        for trigger in counts:
            counts[trigger] = counts[trigger].GetValue()
        for trigger in counts:
            if counts[trigger] == 0:
                unprescaledTriggers.append(trigger)
            else:
                prescaledTriggers.append(trigger)
        

        self.triggerTables = {
            'unprescaledTriggers': unprescaledTriggers,
            'prescaledTriggers': prescaledTriggers,
        }
        with open(self.jsonLocation, 'w+') as theFile:
            json.dump(
                self.triggerTables,
                theFile,
                indent=4,
            )

    def getNoOverlapString(self):
        overlapString = ''
        for trigger in self.triggerTables['unprescaledTriggers']:
            overlapString += f'{trigger} == 0 &&'
        overlapString = overlapString[:-2]
        return overlapString
        
    def getOverlapString(self):
        overlapString = ''
        for trigger in self.triggerTables['unprescaledTriggers']:
            overlapString += f'{trigger} == 1 ||'
        overlapString = overlapString[:-2]
        return overlapString
