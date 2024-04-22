from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

import ROOT
from anomalyDetection.paperCode.plottingUtilities.models import *
from pathlib import Path

class createScorePlotTask(createPlotTask):
    def __init__(
            self,
            taskName: str,
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
        
    def createPlots(self):
        sampleNames = list(self.dictOfSamples.keys())
        sampleNames.remove('ZeroBias')
            
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
        scoreNames.append(toyHTModel.scoreName)
        scoreNames.append("CICADA_v2p1p2")
        scoreNames.append(CICADAInputScore.scoreName)

        evenLumiZBDataframe, oddLumiZBDataframe = self.makeTrainTestDataframes(self.dictOfSamples['ZeroBias'])
        
        #assemble all dataframes
        allDFs = {
            'Train_ZeroBias': evenLumiZBDataframe,
            'Test_ZeroBias': oddLumiZBDataframe,
        }
        for sampleName in self.dictOfSamples:
            if sampleName == 'ZeroBias':
                continue
            allDFs[sampleName] = self.dictOfSamples[sampleName].getNewDataframe()
        for sampleName in allDFs:
            allDFs[sampleName] = toyHTModel.applyFrameDefinitions(allDFs[sampleName])
            allDFs[sampleName] = CICADAInputScore.applyFrameDefinitions(allDFs[sampleName])
            for group in cicadaScoreGroups:
                allDFs[sampleName] = group.applyFrameDefinitions(allDFs[sampleName])
        
        #let's get the minimum and maximum values for each of our scores
        scoreMaxes, scoreMins = self.getScoreMaxesAndMins(scoreNames, allDFs)

        for sampleName in allDFs:
            theDataframe = allDFs[sampleName]
            #self.console.log(f'{sampleName}')
            thePlots = self.makePlotsForScores(
                theDataframe,
                scoreNames,
                sampleName,
                nBins = self.nBins,
                scoreMaxes = scoreMaxes,
                scoreMins = scoreMins
            )
            self.plotsToBeWritten += thePlots

    def makePlotsForScores(self, theDataframe, listOfScores, baseName, nBins, scoreMaxes, scoreMins):
        resultPlots = []
        for scoreName in listOfScores:
            # The use of xx is a delimter inbetween important parts of the name
            histName = f'{baseName}_xxx_{scoreName}'
            theModel = ROOT.RDF.TH1DModel(
                histName,
                histName,
                nBins,
                scoreMaxes[scoreName],
                scoreMins[scoreName],
            )
            resultPlots.append(theDataframe.Histo1D(theModel, scoreName))
        return resultPlots

    #this may be expensive enough that we want to think about a way to cache this on disk
    #this can be at the very least restructured to bookings before calling values.
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
        

    #makes dataframes representing the train and test set
    # even lumi: training
    # odd lumi: test
    def makeTrainTestDataframes(self, zeroBiasSample):
        zeroBiasDataframe = zeroBiasSample.getNewDataframe()
        evenLumiZBDataframe = zeroBiasDataframe.Filter('lumi % 2 == 0')
        oddLumiZBDataframe = zeroBiasDataframe.Filter('lumi % 2 == 1')
        
        return evenLumiZBDataframe, oddLumiZBDataframe
    
    def makeAllScoreNamesFromGroups(self, listOfGroups):
        scoreNameList = []
        for group in listOfGroups:
            scoreNameList.append(group.teacherModel.scoreName)
            for studentModelName in group.studentModels:
                scoreNameList.append(group.studentModels[studentModelName].scoreName)
        return scoreNameList
