from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

import ROOT
from anomalyDetection.paperCode.plottingUtilities.models import *
from pathlib import Path
from anomalyDetection.paperCode.plottingUtilities.scoreMaxAndMins import scoreMaxAndMinHelper
from anomalyDetection.paperCode.plottingUtilities.rateTables import rateTableHelper


class createCICADATurnOnPlotTask(createPlotTask):
    def __init__(
            self,
            taskName: str,
            outputFileName: str,
            dictOfSamples: dict,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/"),
            nBins: int = 40,
            rates: list[float] = [3.0,],
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
        self.rates = rates

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
            "HT",
        ]

        scoreNames = self.makeAllScoreNamesFromGroups(cicadaScoreGroups)
        scoreNames.append("CICADA_v2p1p2")

        dictOfDataframes = {}
        for sampleName in self.dictOfSamples:
            dictOfDataframes[sampleName] = self.dictOfSamples[sampleName].getNewDataframe()
            dictOfDataframes[sampleName] = toyHTModel.applyFrameDefinitions(dictOfDataframes[sampleName])
            for scoreGroup in cicadaScoreGroups:
                dictOfDataframes[sampleName] = scoreGroup.applyFrameDefinitions(dictOfDataframes[sampleName])

        scoreMaxes, scoreMins = self.scoreMaxAndMins.getScoreMaxesAndMins(scoreNames, dictOfDataframes)
        secondaryMaxes, secondaryMins =self.getScoreMaxesAndMins(secondaryVariables, dictOfDataframes)

        # okay, how do we do trigger turn ons?
        #A typical trigger turn on is a variable, and %trigger fires out of total
        # Let's start with HT
        #I think the plot on this is just a 2D score plot frankly
        #And then we row integrate in the drawing script
        for sampleName in dictOfDataframes:
            for variable in secondaryVariables:
                plots = self.makeScoresVsVariablePlot(
                    dataframe = dictOfDataframes[sampleName],
                    sample = sampleName,
                    scores = scoreNames,
                    secondaryVariable = variable,
                    scoreMaxes = scoreMaxes,
                    scoreMins = scoreMins,
                    secondaryVariableMax = secondaryMaxes[variable],
                    secondaryVariableMin = secondaryMins[variable],
                )
                self.plotsToBeWritten += plots

        #okay. We need to redo the trigger turn ons to work in 1D
        #How do we do that?
        #We get the dataframe corresponding to our desired rate
        #And we get a dataframe that is total
        #We make two plots of the secondary variable
        #Then later we divide

        #yikes
        for rate in self.rates:
            for sampleName in dictOfDataframes:
                for variable in secondaryVariables:
                    for score in scoreNames:
                        rateThreshold, trueRate = self.rateTable.getThresholdForRate(score, rate)
                        rateDF = dictOfDataframes[sampleName].Filter(f'{score} > {rateThreshold}')
                        rateHist, totalHist = self.make1DScoresVsVariablePlot(dictOfDataframes[sampleName], rateDF, sampleName, score, variable, secondaryMaxes[variable], secondaryMins[variable], rate)
                        self.plotsToBeWritten += [rateHist, totalHist]

    def make1DScoresVsVariablePlot(self, totalDF, rateDF, sample, score, secondaryVariable, variableMax, variableMin, rate):
        rateStr = str(rate).replace('.','p')
        rateName = f"{sample}_xxx_{score}_xxx_{secondaryVariable}_xxx_1D_xxx_{rateStr}"
        totalName = f"{sample}_xxx_{score}_xxx_{secondaryVariable}_xxx_1D_xxx_total"
        rateModel = ROOT.RDF.TH1DModel(
            rateName,
            rateName,
            self.nBins,
            variableMin,
            variableMax,
        )
        totalModel = ROOT.RDF.TH1DModel(
            totalName,
            totalName,
            self.nBins,
            variableMin,
            variableMax,
        )
        rateHist = rateDF.Histo1D(rateModel, secondaryVariable)
        totalHist = totalDF.Histo1D(totalModel, secondaryVariable)
        return rateHist, totalHist

    def makeScoresVsVariablePlot(self, dataframe, sample, scores, secondaryVariable, scoreMaxes, scoreMins, secondaryVariableMax, secondaryVariableMin):
        resultPlots = []
        for score in scores:
            histName = f"{sample}_xxx_{score}_xxx_{secondaryVariable}"
            theModel = ROOT.RDF.TH2DModel(
                histName,
                histName,
                self.nBins,
                scoreMins[score],
                scoreMaxes[score],
                self.nBins,
                secondaryVariableMin,
                secondaryVariableMax,
            )
            resultPlots.append(dataframe.Histo2D(theModel, score, secondaryVariable))
        return resultPlots
    
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
