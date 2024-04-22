from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

import ROOT
from anomalyDetection.paperCode.plottingUtilities.models import *
from pathlib import Path

class createHTCorrelationPlotTask(createPlotTask):
    def __init__(
            self,
            taskName: str,
            outputFileName: str,
            dictOfSamples: dict,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/")
    ):
        super().__init__(
            taskName,
            outputFileName,
            dictOfSamples,
            outputPath,
        )

    def createPlots(self):        
        cicadaScoreGroups = [
            CICADA_vXp2p0_Group,
            CICADA_vXp2p0N_Group,
            CICADA_vXp2p1_Group,
            CICADA_vXp2p1N_Group,
            CICADA_vXp2p2_Group,
            CICADA_vXp2p2N_Group,
            GADGET_v1p0p0_Group,
        ]
        
        scoreNames = self.makeAllScoreNamesFromGroups(cicadaScoreGroups)
        scoreNames.append("CICADA_v2p1p2")
        
        dictOfDataframes = {}
        for sampleName in self.dictOfSamples:
            dictOfDataframes[sampleName] = self.dictOfSamples[sampleName].getNewDataframe()
            dictOfDataframes[sampleName] = toyHTModel.applyFrameDefinitions(dictOfDataframes[sampleName])

        scoreMaxes, scoreMins = self.getScoreMaxesAndMins(scoreNames, dictOfDataframes)
        HTMax, HTMin = self.getHTMaxAndMin(dictOfDataframes)

        for sampleName in dictOfDataframes:
            #listOfFiles = self.dictOfSamples["sampleName"].listOfFiles
            #self.console.log(f'{sampleName}: {len(listOfFiles):>6d} Files')
            
            theDataframe = dictOfDataframes[sampleName]
            self.plotsToBeWritten += self.makeHTPlotsForDataframe(
                theDataframe,
                scoreNames,
                sampleName,
                scoreMaxes,
                scoreMins,
                HTMax,
                HTMin
            )

    def getHTMaxAndMin(self, sampleDataframes):
        #self.console.log("Calculating HT max and min")
        possibleMaxes = []
        possibleMins = []
        for sample in sampleDataframes:
            possibleMaxes.append(sampleDataframes[sample].Max("HT"))
            possibleMins.append(sampleDataframes[sample].Min("HT"))
        for index in range(len(possibleMaxes)):
            possibleMaxes[index] = possibleMaxes[index].GetValue()
        for index in range(len(possibleMins)):
            possibleMins[index] = possibleMins[index].GetValue()
        return max(possibleMaxes), min(possibleMins)
        

    def getScoreMaxesAndMins(self, scores, sampleDataframes):
        #self.console.log("Calculating score max and min")
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
                possibleMins.append(sampleMaxes[sample][score])
            scoreMaxes[score] = max(possibleMaxes)
            scoreMins[score] = min(possibleMins)
        return scoreMaxes, scoreMins

    def makeHTPlotsForDataframe(self, theDataframe, listOfScores, sampleName, scoreMaxes, scoreMins, HTMax, HTMin, nBins=100):
        resultPlots = []
        for scoreName in listOfScores:
            # The use of xx is a delimter inbetween important parts of the name
            histoName = f'{sampleName}_xxx_{scoreName}_xxx_HT'
            histoModel = ROOT.RDF.TH2DModel(
                histoName,
                histoName,
                nBins,
                scoreMins[scoreName],
                scoreMaxes[scoreName],
                nBins,
                HTMin,
                HTMax
            )
            thePlot = theDataframe.Histo2D(
                histoModel,
                scoreName,
                "HT",
            )
            resultPlots.append(thePlot)
        return resultPlots

    def makeAllScoreNamesFromGroups(self, listOfGroups):
        scoreNameList = []
        for group in listOfGroups:
            scoreNameList.append(group.teacherModel.scoreName)
            for studentModelName in group.studentModels:
                scoreNameList.append(group.studentModels[studentModelName].scoreName)
        return scoreNameList
