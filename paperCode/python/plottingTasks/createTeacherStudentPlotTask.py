from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

import ROOT
from anomalyDetection.paperCode.plottingUtilities.models import *
from pathlib import Path
from anomalyDetection.paperCode.plottingUtilities.scoreMaxAndMins import scoreMaxAndMinHelper

import os

import json

class createTeacherStudentPlotTask(createPlotTask):
    def __init__(
            self,
            taskName: str,
            outputFileName: str,
            dictOfSamples: dict,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/"),
            maxMinCachePath: Path = Path(f"{os.environ['CMSSW_BASE']}/src/anomalyDetection/paperCode/metadata/teacherStudentMaxMinCalculation.json")
    ):
        super().__init__(
            taskName,
            outputFileName,
            dictOfSamples,
            outputPath,
        )
        self.scoreMaxAndMins = scoreMaxAndMinHelper()
        self.maxMinCachePath = maxMinCachePath
        self.maxes, self.mins = self.loadMaxesAndMins()

    def loadMaxesAndMins(self):
        try:
            theFile = open(self.maxMinCachePath)
            data = json.load(theFile)
        except FileNotFoundError:
            return {}, {}
        else:
            return data['maxes'], data['mins']

    def createDeltaScatter(self, frame, sampleName, theTeacherStudentPair, adjustedTeacherScoreMax, adjustedTeacherScoreMin, deltaMax, deltaMin):
        # the xxx is a delimeter between important parts of the name
        histoName = f'{sampleName}_xxx_{theTeacherStudentPair.teacherModel.modelName}_xxx_{theTeacherStudentPair.studentModel.modelName}_xxx_delta_scatter'
        scatterModel = ROOT.RDF.TH2DModel(
            histoName,
            histoName,
            20,
            adjustedTeacherScoreMin,
            adjustedTeacherScoreMax,
            20,
            deltaMin,
            deltaMax,
        )

        scatterBooking = frame.Histo2D(
            scatterModel,
            theTeacherStudentPair.adjustedTeacherScoreName,
            theTeacherStudentPair.studentScoreDeltaName,
        )

        return scatterBooking

    def createAbsDeltaScatter(self, frame, sampleName, theTeacherStudentPair, adjustedTeacherScoreMax, adjustedTeacherScoreMin, absDeltaMax, absDeltaMin):
        # the xxx is a delimeter between important parts of the name
        histoName = f"{sampleName}_xxx_{theTeacherStudentPair.teacherModel.modelName}_xxx_{theTeacherStudentPair.studentModel.modelName}_xxx_abs_delta_scatter"
        scatterModel = ROOT.RDF.TH2DModel(
            histoName,
            histoName,
            20,
            adjustedTeacherScoreMin,
            adjustedTeacherScoreMax,
            20,
            absDeltaMin,
            absDeltaMax,
        )

        scatterBooking = frame.Histo2D(
            scatterModel,
            theTeacherStudentPair.adjustedTeacherScoreName,
            theTeacherStudentPair.absStudentScoreDeltaName,
        )
        return scatterBooking

    def createTeacherAdjustedScorePlot(self, frame, sampleName, theTeacherStudentCollection, adjustedTeacherScoreMax, adjustedTeacherScoreMin):
        # the xxx is a delimeter between important parts of the name
        histoName = f"{sampleName}_xxx_{theTeacherStudentCollection.teacherModel.modelName}_xxx_teacher_adjusted_score"
        scoreModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            50,
            adjustedTeacherScoreMin,
            adjustedTeacherScoreMax,
        )

        scoreBooking = frame.Histo1D(
            scoreModel,
            theTeacherStudentCollection.adjustedTeacherScoreName
        )
        return scoreBooking

    def createTeacherScorePlot(self, frame, sampleName, theTeacherStudentCollection, teacherScoreMax, teacherScoreMin):
        histoName = f"{sampleName}_xxx_{theTeacherStudentCollection.teacherModel.modelName}_xxx_teacher_score"
        scoreModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName, 
            50,
            teacherScoreMin,
            teacherScoreMax,
        )

        scoreBooking = frame.Histo1D(
            scoreModel,
            theTeacherStudentCollection.teacherModel.scoreName,
        )
        
        return scoreBooking

    def createStudentScorePlot(self, frame, sampleName, theTeacherStudentPair, studentScoreMax, studentScoreMin):
        histoName = f"{sampleName}_xxx_{theTeacherStudentPair.studentModel.modelName}_xxx_student_score"
        scoreModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            50,
            studentScoreMin,
            studentScoreMax,
        )

        scoreBooking = frame.Histo1D(
            scoreModel,
            theTeacherStudentPair.studentModel.scoreName
        )
        return scoreBooking

    def createStudentErrorHist(self, frame, sampleName, theTeacherStudentPair, studentErrorMax, studentErrorMin):
        histoName = f"{sampleName}_xxx_{theTeacherStudentPair.teacherModel.modelName}_xxx_{theTeacherStudentPair.studentModel.modelName}_xxx_student_errors"
        errorModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            50,
            studentErrorMin,
            studentErrorMax,
        )

        errorBooking = frame.Histo1D(
            errorModel,
            theTeacherStudentPair.studentScoreDeltaName,
        )

        return errorBooking

    def createStudentAbsErrorHist(self, frame, sampleName, theTeacherStudentPair, absStudentErrorMax, absStudentErrorMin):
        histoName =f"{sampleName}_xxx_{theTeacherStudentPair.teacherModel.modelName}_xxx_{theTeacherStudentPair.studentModel.modelName}_xxx_student_abs_errors"
        errorModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            50,
            absStudentErrorMin,
            absStudentErrorMax,
        )

        errorBooking = frame.Histo1D(
            errorModel,
            theTeacherStudentPair.absStudentScoreDeltaName
        )
        
        return errorBooking

    def bookPlots(self, dataframe, sampleName, teacherStudentModels, maxes, mins):
        plots = []
        for teacherStudentGroup in teacherStudentModels:
            plots.append(
                self.createTeacherAdjustedScorePlot(
                    dataframe,
                    sampleName,
                    teacherStudentGroup,
                    maxes[teacherStudentGroup.adjustedTeacherScoreName],
                    mins[teacherStudentGroup.adjustedTeacherScoreName],
                )
            )
            plots.append(
                self.createTeacherScorePlot(
                    dataframe,
                    sampleName,
                    teacherStudentGroup,
                    maxes[teacherStudentGroup.teacherModel.scoreName],
                    mins[teacherStudentGroup.teacherModel.scoreName],
                )
            )
            for theTeacherStudentPair in teacherStudentGroup.teacherStudentPairs:
                plots.append(
                    self.createDeltaScatter(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.adjustedTeacherScoreName],
                        mins[theTeacherStudentPair.adjustedTeacherScoreName],
                        maxes[theTeacherStudentPair.studentScoreDeltaName],
                        mins[theTeacherStudentPair.studentScoreDeltaName],
                    )
                )
                plots.append(
                    self.createAbsDeltaScatter(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.adjustedTeacherScoreName],
                        mins[theTeacherStudentPair.adjustedTeacherScoreName],
                        maxes[theTeacherStudentPair.absStudentScoreDeltaName],
                        mins[theTeacherStudentPair.absStudentScoreDeltaName],
                    )
                )
                plots.append(
                    self.createStudentScorePlot(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.studentModel.scoreName],
                        mins[theTeacherStudentPair.studentModel.scoreName],
                    )
                )
                plots.append(
                    self.createStudentErrorHist(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.studentScoreDeltaName],
                        mins[theTeacherStudentPair.studentScoreDeltaName],
                    )
                )
                plots.append(
                    self.createStudentAbsErrorHist(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.absStudentScoreDeltaName],
                        mins[theTeacherStudentPair.absStudentScoreDeltaName],
                    )
                )
        return plots

    def getMaxesAndMins(self, dataframes, teacherStudentGroups):
        #this is lazy, but I don't want to deal with the logic of rewriting what
        #needs to be calculated or not.
        #just cache the result, and move on
        #But this will likely mean that we have to remember to clear that cache
        #If and when the list of scores we care about updates
        if self.maxes == {} or self.mins == {}: 
            self.maxes, self.mins = self.calculateMaxesAndMins(dataframes, teacherStudentGroups)
            with open(self.maxMinCachePath) as theFile:
                json.dump(
                    {
                        'maxes': self.maxes,
                        'mins': self.mins,
                    },
                    theFile
                )
        return self.maxes, self.mins

    def calculateMaxesAndMins(self, dataframes, teacherStudentGroups):
        overallMaxes= {}
        overallMins={}

        possibleMaxes = {}
        possibleMins = {}
        for teacherStudentGroup in teacherStudentGroups:
            possibleMaxes[teacherStudentGroup.adjustedTeacherScoreName] = {}
            possibleMaxes[teacherStudentGroup.teacherModel.scoreName] = {}
            possibleMins[teacherStudentGroup.adjustedTeacherScoreName] = {}
            possibleMins[teacherStudentGroup.teacherModel.scoreName] = {}
            for sampleName in dataframes:
                theDataframe = dataframes[sampleName]
                possibleMaxes[teacherStudentGroup.adjustedTeacherScoreName][sampleName] = theDataframe.Max(teacherStudentGroup.adjustedTeacherScoreName)
                possibleMins[teacherStudentGroup.adjustedTeacherScoreName][sampleName] = theDataframe.Min(teacherStudentGroup.adjustedTeacherScoreName)
                possibleMaxes[teacherStudentGroup.teacherModel.scoreName][sampleName] = theDataframe.Max(teacherStudentGroup.teacherModel.scoreName)
                possibleMins[teacherStudentGroup.teacherModel.scoreName][sampleName] = theDataframe.Min(teacherStudentGroup.teacherModel.scoreName)

            for teacherStudentPair in teacherStudentGroup.teacherStudentPairs:
                possibleMaxes[teacherStudentPair.studentScoreDeltaName] = {}
                possibleMaxes[teacherStudentPair.absStudentScoreDeltaName] = {}
                possibleMaxes[teacherStudentPair.studentModel.scoreName] = {}
                possibleMins[teacherStudentPair.studentScoreDeltaName] = {}
                possibleMins[teacherStudentPair.absStudentScoreDeltaName] = {}
                possibleMins[teacherStudentPair.studentModel.scoreName] = {}

                for sampleName in dataframes:
                    theDataframe = dataframes[sampleName]
                    possibleMaxes[teacherStudentPair.studentScoreDeltaName][sampleName] = theDataframe.Max(teacherStudentPair.studentScoreDeltaName)
                    possibleMins[teacherStudentPair.studentScoreDeltaName][sampleName] = theDataframe.Min(teacherStudentPair.studentScoreDeltaName)
                    possibleMaxes[teacherStudentPair.absStudentScoreDeltaName][sampleName] = theDataframe.Max(teacherStudentPair.absStudentScoreDeltaName)
                    possibleMins[teacherStudentPair.absStudentScoreDeltaName][sampleName] = theDataframe.Min(teacherStudentPair.absStudentScoreDeltaName)
                    possibleMaxes[teacherStudentPair.studentModel.scoreName][sampleName] = theDataframe.Max(teacherStudentPair.studentModel.scoreName)
                    possibleMins[teacherStudentPair.studentModel.scoreName][sampleName] = theDataframe.Min(teacherStudentPair.studentModel.scoreName)
        #After the nightmare of booking all those result vectors, we calculate the
        # actual values we need to use
        for teacherStudentGroup in teacherStudentGroups:
            for sampleName in dataframes:
                possibleMaxes[teacherStudentGroup.adjustedTeacherScoreName][sampleName] = possibleMaxes[teacherStudentGroup.adjustedTeacherScoreName][sampleName].GetValue()
                possibleMins[teacherStudentGroup.adjustedTeacherScoreName][sampleName] = possibleMins[teacherStudentGroup.adjustedTeacherScoreName][sampleName].GetValue()
                possibleMaxes[teacherStudentGroup.teacherModel.scoreName][sampleName] = possibleMaxes[teacherStudentGroup.teacherModel.scoreName][sampleName].GetValue()
                possibleMins[teacherStudentGroup.teacherModel.scoreName][sampleName] = possibleMins[teacherStudentGroup.teacherModel.scoreName][sampleName].GetValue()
            
            for teacherStudentPair in teacherStudentGroup.teacherStudentPairs:
                for sampleName in dataframes:
                    possibleMaxes[teacherStudentPair.studentScoreDeltaName][sampleName] = possibleMaxes[teacherStudentPair.studentScoreDeltaName][sampleName].GetValue()
                    possibleMins[teacherStudentPair.studentScoreDeltaName][sampleName] = possibleMins[teacherStudentPair.studentScoreDeltaName][sampleName].GetValue()
                    possibleMaxes[teacherStudentPair.absStudentScoreDeltaName][sampleName] = possibleMaxes[teacherStudentPair.absStudentScoreDeltaName][sampleName].GetValue()
                    possibleMins[teacherStudentPair.absStudentScoreDeltaName][sampleName] = possibleMins[teacherStudentPair.absStudentScoreDeltaName][sampleName].GetValue()
                    possibleMaxes[teacherStudentPair.studentModel.scoreName][sampleName] = possibleMaxes[teacherStudentPair.studentModel.scoreName][sampleName].GetValue()
                    possibleMins[teacherStudentPair.studentModel.scoreName][sampleName] = possibleMins[teacherStudentPair.studentModel.scoreName][sampleName].GetValue()

        #okay. Now we need to get the genuine maxes
        for teacherStudentGroup in teacherStudentGroups:
            overallMaxes[teacherStudentGroup.adjustedTeacherScoreName], overallMins[teacherStudentGroup.adjustedTeacherScoreName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentGroup.adjustedTeacherScoreName)
            overallMaxes[teacherStudentGroup.teacherModel.scoreName], overallMins[teacherStudentGroup.teacherModel.scoreName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentGroup.teacherModel.scoreName)
            for teacherStudentPair in teacherStudentGroup.teacherStudentPairs:
                overallMaxes[teacherStudentPair.studentScoreDeltaName], overallMins[teacherStudentPair.studentScoreDeltaName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentPair.studentScoreDeltaName)
                overallMaxes[teacherStudentPair.absStudentScoreDeltaName], overallMins[teacherStudentPair.absStudentScoreDeltaName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentPair.absStudentScoreDeltaName)
                overallMaxes[teacherStudentPair.studentModel.scoreName], overallMins[teacherStudentPair.studentModel.scoreName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentPair.studentModel.scoreName)

        return overallMaxes, overallMins

    def getMaxAndMinFromPossibles(self, possibleMaxes, possibleMins, name):
        maxList = []
        minList = []
        for sampleName in possibleMaxes[name]:
            maxList.append(possibleMaxes[name][sampleName])
            minList.append(possibleMins[name][sampleName])
        return max(maxList), min(minList)
            
    def createPlots(self):
        sampleNames = list(self.dictOfSamples.keys())

        teacherStudentModels = [
            CICADA_vXp2p0_Group,
            CICADA_vXp2p0N_Group,
            CICADA_vXp2p1_Group,
            CICADA_vXp2p1N_Group,
            CICADA_vXp2p2_Group,
            CICADA_vXp2p2N_Group,
        ]

        dictOfDataframes = {}
        for sampleName in sampleNames:
            dictOfDataframes[sampleName] = self.dictOfSamples[sampleName].getNewDataframe()
            for teacherStudentGroup in teacherStudentModels:
                dictOfDataframes[sampleName] = teacherStudentGroup.applyFrameDefinitions(dictOfDataframes[sampleName])
        
        maxes, mins = self.getMaxesAndMins(dictOfDataframes, teacherStudentModels)

        for sampleName in dictOfDataframes:
            #console.log(f"{sampleName}")
            frame = dictOfDataframes[sampleName]
            plots = self.bookPlots(frame, sampleName, teacherStudentModels, maxes, mins)
            self.plotsToBeWritten += plots
            

