from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

import ROOT
import math
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

    def createFractionalErrorScatter(self, frame, sampleName, theTeacherStudentPair, adjustedTeacherScoreMax, adjustedTeacherScoreMin, fractionalErrorMax, fractionalErrorMin):
        #print("Making booking")
        histoName = f"{sampleName}_xxx_{theTeacherStudentPair.studentFractionalErrorName}_xxx_{theTeacherStudentPair.studentModel.modelName}_xxx_fractional_delta_scatter"
        scatterModel = ROOT.RDF.TH2DModel(
            histoName,
            histoName,
            20,
            adjustedTeacherScoreMin,
            adjustedTeacherScoreMax,
            20,
            fractionalErrorMin,
            fractionalErrorMax,
        )

        theBooking = frame.Histo2D(
            scatterModel,
            theTeacherStudentPair.adjustedTeacherScoreName,
            theTeacherStudentPair.studentFractionalErrorName,
        )
        #print("Done!")
        return theBooking

    def createAbsFractionalErrorScatter(self, frame, sampleName, theTeacherStudentPair, adjustedTeacherScoreMax, adjustedTeacherScoreMin, absFractionalErrorMax, absFractionalErrorMin):
        histoName = f"{sampleName}_xxx_{theTeacherStudentPair.studentFractionalErrorName}_xxx_{theTeacherStudentPair.studentModel.modelName}_xxx_abs_fractional_delta_scatter"
        scatterModel = ROOT.RDF.TH2DModel(
            histoName,
            histoName,
            20,
            adjustedTeacherScoreMin,
            adjustedTeacherScoreMax,
            20,
            absFractionalErrorMin,
            absFractionalErrorMax,
        )

        theBooking = frame.Histo2D(
            scatterModel,
            theTeacherStudentPair.adjustedTeacherScoreName,
            theTeacherStudentPair.absStudentFractionalErrorName
        )
        return theBooking

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
            #print("Adjusted teacher")
            plots.append(
                self.createTeacherAdjustedScorePlot(
                    dataframe,
                    sampleName,
                    teacherStudentGroup,
                    maxes[teacherStudentGroup.adjustedTeacherScoreName],
                    mins[teacherStudentGroup.adjustedTeacherScoreName],
                )
            )
            #print("teacher")
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
                #print("Delta")
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
                #print("Abs delta")
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
                #print("Student score")
                plots.append(
                    self.createStudentScorePlot(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.studentModel.scoreName],
                        mins[theTeacherStudentPair.studentModel.scoreName],
                    )
                )
                #print("Student error")
                plots.append(
                    self.createStudentErrorHist(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.studentScoreDeltaName],
                        mins[theTeacherStudentPair.studentScoreDeltaName],
                    )
                )
                #print("student abs error")
                plots.append(
                    self.createStudentAbsErrorHist(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.absStudentScoreDeltaName],
                        mins[theTeacherStudentPair.absStudentScoreDeltaName],
                    )
                )
                #print("fractional error")
                #print(theTeacherStudentPair.adjustedTeacherScoreName)
                #print(theTeacherStudentPair.studentFractionalErrorName)
                #print(maxes)
                #print(mins)
                #print(maxes[theTeacherStudentPair.adjustedTeacherScoreName])
                #print(mins[theTeacherStudentPair.adjustedTeacherScoreName])
                #print(maxes[theTeacherStudentPair.studentFractionalErrorName])
                #print(mins[theTeacherStudentPair.studentFractionalErrorName])
                plots.append(
                    self.createFractionalErrorScatter(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.adjustedTeacherScoreName],
                        mins[theTeacherStudentPair.adjustedTeacherScoreName],
                        maxes[theTeacherStudentPair.studentFractionalErrorName],
                        mins[theTeacherStudentPair.studentFractionalErrorName],
                    )
                )
                #print("abs fractional error")
                plots.append(
                    self.createAbsFractionalErrorScatter(
                        dataframe,
                        sampleName,
                        theTeacherStudentPair,
                        maxes[theTeacherStudentPair.adjustedTeacherScoreName],
                        mins[theTeacherStudentPair.adjustedTeacherScoreName],
                        maxes[theTeacherStudentPair.absStudentFractionalErrorName],
                        mins[theTeacherStudentPair.absStudentFractionalErrorName],
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
            with open(self.maxMinCachePath, 'w+') as theFile:
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
        #print("Calculating")
        for teacherStudentGroup in teacherStudentGroups:
            #print("teacher scores")
            possibleMaxes[teacherStudentGroup.adjustedTeacherScoreName] = {}
            possibleMaxes[teacherStudentGroup.teacherModel.scoreName] = {}
            possibleMins[teacherStudentGroup.adjustedTeacherScoreName] = {}
            possibleMins[teacherStudentGroup.teacherModel.scoreName] = {}
            for sampleName in dataframes:
                #print(sampleName)
                theDataframe = dataframes[sampleName]
                possibleMaxes[teacherStudentGroup.adjustedTeacherScoreName][sampleName] = theDataframe.Max(teacherStudentGroup.adjustedTeacherScoreName)
                possibleMins[teacherStudentGroup.adjustedTeacherScoreName][sampleName] = theDataframe.Min(teacherStudentGroup.adjustedTeacherScoreName)
                possibleMaxes[teacherStudentGroup.teacherModel.scoreName][sampleName] = theDataframe.Max(teacherStudentGroup.teacherModel.scoreName)
                possibleMins[teacherStudentGroup.teacherModel.scoreName][sampleName] = theDataframe.Min(teacherStudentGroup.teacherModel.scoreName)

            #print("teacher student pairs")
            for teacherStudentPair in teacherStudentGroup.teacherStudentPairs:
                possibleMaxes[teacherStudentPair.studentScoreDeltaName] = {}
                possibleMaxes[teacherStudentPair.absStudentScoreDeltaName] = {}
                possibleMaxes[teacherStudentPair.studentModel.scoreName] = {}
                possibleMaxes[teacherStudentPair.studentFractionalErrorName] = {}
                possibleMaxes[teacherStudentPair.absStudentFractionalErrorName] = {}
                possibleMins[teacherStudentPair.studentScoreDeltaName] = {}
                possibleMins[teacherStudentPair.absStudentScoreDeltaName] = {}
                possibleMins[teacherStudentPair.studentModel.scoreName] = {}
                possibleMins[teacherStudentPair.studentFractionalErrorName] = {}
                possibleMins[teacherStudentPair.absStudentFractionalErrorName] = {}

                for sampleName in dataframes:
                    #print(sampleName)
                    theDataframe = dataframes[sampleName]
                    #print(teacherStudentPair.studentScoreDeltaName)
                    possibleMaxes[teacherStudentPair.studentScoreDeltaName][sampleName] = theDataframe.Max(teacherStudentPair.studentScoreDeltaName)
                    possibleMins[teacherStudentPair.studentScoreDeltaName][sampleName] = theDataframe.Min(teacherStudentPair.studentScoreDeltaName)
                    #print(teacherStudentPair.absStudentScoreDeltaName)
                    possibleMaxes[teacherStudentPair.absStudentScoreDeltaName][sampleName] = theDataframe.Max(teacherStudentPair.absStudentScoreDeltaName)
                    possibleMins[teacherStudentPair.absStudentScoreDeltaName][sampleName] = theDataframe.Min(teacherStudentPair.absStudentScoreDeltaName)
                    #print(teacherStudentPair.studentModel.scoreName)
                    possibleMaxes[teacherStudentPair.studentModel.scoreName][sampleName] = theDataframe.Max(teacherStudentPair.studentModel.scoreName)
                    possibleMins[teacherStudentPair.studentModel.scoreName][sampleName] = theDataframe.Min(teacherStudentPair.studentModel.scoreName)
                    
                    #print(teacherStudentPair.studentFractionalErrorName)
                    possibleMaxes[teacherStudentPair.studentFractionalErrorName][sampleName] = theDataframe.Max(teacherStudentPair.studentFractionalErrorName)
                    possibleMins[teacherStudentPair.studentFractionalErrorName][sampleName] = theDataframe.Min(teacherStudentPair.studentFractionalErrorName)
                    #print(teacherStudentPair.absStudentFractionalErrorName)
                    possibleMaxes[teacherStudentPair.absStudentFractionalErrorName][sampleName] = theDataframe.Max(teacherStudentPair.absStudentFractionalErrorName)
                    possibleMins[teacherStudentPair.absStudentFractionalErrorName][sampleName] = theDataframe.Min(teacherStudentPair.absStudentFractionalErrorName)
        #After the nightmare of booking all those result vectors, we calculate the
        # actual values we need to use
        #print("Getting values")
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

                    possibleMaxes[teacherStudentPair.studentFractionalErrorName][sampleName] = possibleMaxes[teacherStudentPair.studentFractionalErrorName][sampleName].GetValue()
                    possibleMins[teacherStudentPair.studentFractionalErrorName][sampleName] = possibleMins[teacherStudentPair.studentFractionalErrorName][sampleName].GetValue()
                    possibleMaxes[teacherStudentPair.absStudentFractionalErrorName][sampleName] = possibleMaxes[teacherStudentPair.absStudentFractionalErrorName][sampleName].GetValue()
                    possibleMins[teacherStudentPair.absStudentFractionalErrorName][sampleName] = possibleMins[teacherStudentPair.absStudentFractionalErrorName][sampleName].GetValue()

        #okay. Now we need to get the genuine maxes
        #print("Genuine maxes")
        for teacherStudentGroup in teacherStudentGroups:
            overallMaxes[teacherStudentGroup.adjustedTeacherScoreName], overallMins[teacherStudentGroup.adjustedTeacherScoreName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentGroup.adjustedTeacherScoreName)
            overallMaxes[teacherStudentGroup.teacherModel.scoreName], overallMins[teacherStudentGroup.teacherModel.scoreName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentGroup.teacherModel.scoreName)
            for teacherStudentPair in teacherStudentGroup.teacherStudentPairs:
                overallMaxes[teacherStudentPair.studentScoreDeltaName], overallMins[teacherStudentPair.studentScoreDeltaName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentPair.studentScoreDeltaName)
                overallMaxes[teacherStudentPair.absStudentScoreDeltaName], overallMins[teacherStudentPair.absStudentScoreDeltaName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentPair.absStudentScoreDeltaName)
                overallMaxes[teacherStudentPair.studentModel.scoreName], overallMins[teacherStudentPair.studentModel.scoreName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentPair.studentModel.scoreName)

                overallMaxes[teacherStudentPair.studentFractionalErrorName], overallMins[teacherStudentPair.studentFractionalErrorName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentPair.studentFractionalErrorName)
                overallMaxes[teacherStudentPair.absStudentFractionalErrorName], overallMins[teacherStudentPair.absStudentFractionalErrorName] = self.getMaxAndMinFromPossibles(possibleMaxes, possibleMins, teacherStudentPair.absStudentFractionalErrorName)
        self.weedOutBadNumbers(overallMaxes, overallMins)
        return overallMaxes, overallMins

    def weedOutBadNumbers(self, maxes, mins):
        for score in maxes:
            if math.isnan(maxes[score]) or math.isinf(maxes[score]):
                maxes[score] = 1000.0
            if math.isnan(mins[score]) or math.isinf(mins[score]):
                mins[score] = -50.0

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
            

