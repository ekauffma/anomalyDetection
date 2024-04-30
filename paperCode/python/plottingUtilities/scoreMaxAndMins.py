from anomalyDetection.paperCode.plottingUtilities.models import *
from pathlib import Path
import json
import os

class scoreMaxAndMinHelper():
    def __init__(
            self,
            jsonLocation: Path = Path(f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/paperCode/metadata/scoreMaxesAndMins.json')
    ):
        self.jsonLocation = jsonLocation
        self.maxes, self.mins = self.loadMaxesAndMins()

    def loadMaxesAndMins(self):
        try:
            theFile = open(self.jsonLocation)
            data = json.load(theFile)
        except FileNotFoundError:
            return {}, {}
        else:
            return data['maxes'], data['mins']

    def getScoreMaxesAndMins(self, scores, sampleDataframes):
        scoresToBeCalculated = []
        for score in scores:
            if (score not in self.maxes) or (score not in self.mins):
                scoresToBeCalculated.append(score)
        if scoresToBeCalculated != []:
            newMaxes, newMins = self.calculateScoreMaxesAndMins(scoresToBeCalculated, sampleDataframes)
            #update the class and the file
            self.maxes.update(newMaxes)
            self.mins.update(newMins)
            with open(self.jsonLocation, 'w+') as theFile:
                json.dump(
                    {
                        'maxes': self.maxes,
                        'mins': self.mins,
                    },
                    theFile
                )
        return self.maxes, self.mins

    def calculateScoreMaxesAndMins(self, scores, sampleDataframes):
        sampleMaxes = {}
        sampleMins = {}
        # book all the calculations up front
        for sample in sampleDataframes:
            sampleDataframe = sampleDataframes[sample]
            sampleMaxes[sample] = {}
            sampleMins[sample] = {}
            for score in scores:
                sampleMaxes[sample][score] = sampleDataframe.Max(score)
                sampleMins[sample][score] = sampleDataframe.Min(score)
        #trigger the actual calculation after all are booked
        for sample in sampleDataframes:
            for score in scores:
                sampleMaxes[sample][score] = sampleMaxes[sample][score].GetValue()
                sampleMins[sample][score] = sampleMins[sample][score].GetValue()

        #now let's get the overall maxes
        scoreMaxes = {}
        scoreMins = {}
        for score in scores:
            possibleMaxes = []
            possibleMins = []
            for sample in sampleDataframes:
                possibleMaxes.append(sampleMaxes[sample][score])
                possibleMins.append(sampleMins[sample][score])
            maxScore = max(possibleMaxes)
            minScore = min(possibleMins)
            scoreMaxes[score] = maxScore
            scoreMins[score] = minScore

        return scoreMaxes, scoreMins
