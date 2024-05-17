from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

import ROOT
from anomalyDetection.paperCode.plottingUtilities.models import *
from pathlib import Path
from anomalyDetection.paperCode.plottingUtilities.scoreMaxAndMins import scoreMaxAndMinHelper

class createSignalAdditionsPlotTask(createPlotTask):
    def __init__(
            self,
            taskName:str,
            outputFileName: str,
            dictOfSamples: dict,
            nBins: int,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/")
    ):
        super().__init__(
            taskName,
            outputFileName,
            dictOfSamples,
            outputPath,
        )
        self.nBins = nBins
        self.scoreMaxAndMins = scoreMaxAndMinHelper()

    def getListOfTriggers(self, sampleDataframe):
        listOfColumns = sampleDataframe.GetColumnNames()
        listOfTriggers = [str(x) for x in listOfColumns if ('L1_' in str(x) and '_prescale' not in str(x))]
        listOfTriggers = [x.split('.')[1] for x in listOfTriggers]
        return listOfTriggers

    def getListOfUnprescaledTriggers(self, sampleDataframe):
        listOfTriggers = self.getListOfTriggers(sampleDataframe)
        #Now we need to check which of these are unprescaled
        counts = {}
        for trigger in listOfTriggers:
            prescaleColumn = f'{trigger}_prescale'
            counts[trigger] = sampleDataframe.Filter(f'{prescaleColumn} != 1').Count()

        for trigger in counts:
            counts[trigger] = counts[trigger].GetValue()
        result = []
        for trigger in counts:
            if counts[trigger] == 0:
                result.append(trigger)
        return result

    def getNoOverlapString(self, listOfUnprescaledTriggers):
        noOverlapString = ''
        for trigger in listOfUnprescaledTriggers:
            noOverlapString += f'{trigger} == 0 &&'
        noOverlapString = noOverlapString[:-2]
        return noOverlapString

    def getOverlapString(self, listOfUnprescaledTriggers):
        overlapString = ''
        for trigger in listOfUnprescaledTriggers:
            overlapString += f'{trigger} == 1 ||'
        overlapString = overlapString[:-2]
        return overlapString

    def noOverlapBooking(self, dataframe, sampleName, score, scoreMin, scoreMax, unprescaledTriggers):
        histoName = f'{sampleName}_xxx_{score}_xxx_NoOverlapWithL1'
        theModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            self.nBins,
            scoreMin,
            scoreMax,
        )
        return dataframe.Filter(self.getNoOverlapString(unprescaledTriggers)).Histo1D(theModel, score)
    
    def overlapBooking(self, dataframe, sampleName, score, scoreMin, scoreMax, unprescaledTriggers):
        histoName = f'{sampleName}_xxx_{score}_xxx_overlapWithL1'
        theModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            self.nBins,
            scoreMin,
            scoreMax,
        )
        return dataframe.Filter(self.getOverlapString(unprescaledTriggers)).Histo1D(theModel, score)

    def genericBooking(self, dataframe, sampleName, score, scoreMin, scoreMax, unprescaledTriggers):
        histoName = f'{sampleName}_xxx_{score}_xxx_all'
        theModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            self.nBins,
            scoreMin,
            scoreMax,
        )
        return dataframe.Histo1D(theModel, score)

    def createPlots(self):
        sampleNames = list(self.dictOfSamples.keys())

        cicadaScoreGroups = [
            CICADA_vXp2p0_Group,
            CICADA_vXp2p0N_Group,
            CICADA_vXp2p1_Group,
            CICADA_vXp2p1N_Group,
            CICADA_vXp2p2_Group,
            CICADA_vXp2p2N_Group,
        ]
        
        scoreNames = self.makeAllScoreNamesFromGroups(cicadaScoreGroups)
        scoreNames.append(toyHTModel.scoreName)
        scoreNames.append("CICADA_v2p1p2")
        scoreNames.append(CICADAInputScore.scoreName)

        allDFs = {}
        for sampleName in self.dictOfSamples:
            allDFs[sampleName] = self.dictOfSamples[sampleName].getNewDataframe()
            allDFs[sampleName] = toyHTModel.applyFrameDefinitions(allDFs[sampleName])
            allDFs[sampleName] = CICADAInputScore.applyFrameDefinitions(allDFs[sampleName])
            for group in cicadaScoreGroups:
                allDFs[sampleName] = group.applyFrameDefinitions(allDFs[sampleName])
            
        #figure out what the unprescaled triggers are
        unprescaledTriggers = self.getListOfUnprescaledTriggers(allDFs['ZeroBias'])
        if 'L1_FirstBunchBeforeTrain' in unprescaledTriggers:
            unprescaledTriggers.remove('L1_FirstBunchBeforeTrain')

        #now that we know what the unprescaled triggers are, we need to figure out what
        #we are getting when we add CICADA, or some other CICADA like thing.
        #how do we want to do that?
        #Three score plots? One CICADA score plot with everything, one with explicit overlaps
        # and one with no overlaps
        #Then when we want signal gain as a function of eff we simply get the eff from the total plot
        #and the additions from the no overlaps plot

        #This means that we need to know the max and min of each score
        scoreMaxes, scoreMins = self.scoreMaxAndMins.getScoreMaxesAndMins()
        
        for sample in allDFs:
            for score in scoreNames:
                self.plotsToBeWritten.append(
                    self.noOverlapBooking(
                        allDFs[sample],
                        sample,
                        score,
                        scoreMins[score],
                        scoreMaxes[score],
                        unprescaledTriggers,
                    )
                )
                self.plotsToBeWritten.append(
                    self.overlapBooking(
                        allDFs[sample],
                        sample,
                        score,
                        scoreMins[score],
                        scoreMaxes[score],
                        unprescaledTriggers,
                    )
                )
                self.plotsToBeWritten.append(
                    self.genericBooking(
                        allDFs[sample],
                        sample,
                        score,
                        scoreMins[score],
                        scoreMaxes[score],
                        unprescaledTriggers,
                    )
                )

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

