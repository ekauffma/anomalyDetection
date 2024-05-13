from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

import ROOT
from anomalyDetection.paperCode.plottingUtilities.models import *
from pathlib import Path
from anomalyDetection.paperCode.plottingUtilities.scoreMaxAndMins import scoreMaxAndMinHelper
from anomalyDetection.paperCode.plottingUtilities.rateTables import rateTableHelper

class createObjectCorrelationPlotsTask(createPlotTask):
    def __init__(
            self,
            taskName: str,
            outputFileName: str,
            dictOfSamples: dict,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/"),
            nBins: int = 30,
    ):
        super().__init__(
            taskName,
            outputFileName,
            dictOfSamples,
            outputPath,
        )
        self.nBins = nBins
        self.scoreMaxAndMins = scoreMaxAndMinHelper()
        self.rateTable = rateTableHelper()

    def createPlots(self):
        cicadaScoreGroups = [
            CICADA_vXp2p0_Group,
            CICADA_vXp2p0N_Group,
            CICADA_vXp2p1_Group,
            CICADA_vXp2p1N_Group,
            CICADA_vXp2p2_Group,
            CICADA_vXp2p2N_Group,
        ]

        secondaryVariables = [
            #Sum stuff
            "HT",
            #EGamma stuff
            "nEGs",
            #"egEt[0]",
            "egEt",
            #Tau stuff
            "nTaus",
            #"tauEt[0]",
            "tauEt",
            #Jet stuff
            "nJets",
            #"jetEt[0]",
            "jetEt",
            #muon stuff
            "nMuons",
            #"muonEt[0]",
            "muonEt",
        ]

        scoreNames = self.makeAllScoreNamesFromGroups(cicadaScoreGroups)
        scoreNames.append("CICADA_v2p1p2")

        dictOfDataframes = {}
        for sampleName in self.dictOfSamples:
            dictOfDataframes[sampleName] = self.dictOfSamples[sampleName].getNewDataframe()
            dictOfDataframes[sampleName] = toyHTModel.applyFrameDefinitions(dictOfDataframes[sampleName])
            for scoreGroup in cicadaScoreGroups:
                dictOfDataframes[sampleName] = scoreGroup.applyFrameDefinitions(dictOfDataframes[sampleName])

        scoreMaxes, scoreMins = self.scoreMaxAndMins.getScoreMaxesAndMins()
        secondaryMaxes, secondaryMins = self.getScoreMaxesAndMins(secondaryVariables, dictOfDataframes)

        for sample in dictOfDataframes:
            for variable in secondaryVariables:
                for score in scoreNames:
                    self.plotsToBeWritten.append(
                        self.make2DScorePlot(
                            dictOfDataframes[sample],
                            sample,
                            score,
                            variable,
                            scoreMaxes[score],
                            scoreMins[score],
                            secondaryMaxes[variable],
                            secondaryMins[variable],
                        )
                    )

    def make2DScorePlot(self, dataframe, sample, score, variable, scoreMax, scoreMin, variableMax, variableMin):
        histoName = f'{sample}_xxx_{score}_xxx_{variable}'
        theModel = ROOT.RDF.TH2DModel(
            histoName,
            histoName,
            self.nBins,
            scoreMin, 
            scoreMax,
            self.nBins,
            variableMin, 
            variableMax,
        )

        return dataframe.Histo2D(theModel, score, variable)

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
                possibleMins.append(sampleMins[sample][score])
            scoreMaxes[score] = max(possibleMaxes)
            scoreMins[score] = min(possibleMins)
        return scoreMaxes, scoreMins

    def makeAllScoreNamesFromGroups(self, listOfGroups):
        scoreNameList = []
        for group in listOfGroups:
            scoreNameList.append(group.adjustedTeacherScoreName)
            for studentModelName in group.studentModels:
                scoreNameList.append(group.studentModels[studentModelName].scoreName)
        return scoreNameList

