# !/usr/bin/env python3

from pathlib import Path
from anomalyDetection.paperCode.plottingCore.plotTask import drawPlotTask
import ROOT
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc

class drawTeacherStudentPlotTask(drawPlotTask):
    def __init__(
            self,
            taskName: str,
            dictOfFiles: list,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/TeacherStudentPlots/")
    ):
        super().__init__(taskName, dictOfFiles, outputPath)

    def parseHistogramName(self, histogramName):
        splitName = histogramName.split('_xxx_')
        sample = None
        teacher = None
        student = None
        plotType = None
        # teacher adjusted scores, teacher scores, student errs, and student abs errs
        sample = splitName[0]
        if len(splitName) == 3:
            plotType = splitName[2]
            if plotType == 'teacher_adjusted_score' or plotType == 'teacher_score':
                teacher = splitName[1]
            elif plotType == 'student_errors' or plotType == 'student_abs_errors' or plotType == 'student_score':
                student = splitName[1]
        #delta scatters, abs delta scatters, 
        elif len(splitName) == 4:
            plotType = splitName[3]
            teacher, student = splitName[1], splitName[2]
        else:
            raise ValueError(f"drawTeacherStudentPlotTask got a name it didn't know how to parse: {histogramName}")
        return sample, teacher, student, plotType
        
    def rowNormalizeHistogram(self, histogram):
        histogramName = f"{histogram.GetName()}_row_norm"
        rowNormHisto = histogram.Clone()
        rowNormHisto.SetNameTitle(
            histogramName,
            histogramName,
        )
        
        nbins_x = rowNormHisto.GetNbinsX()
        nbins_y = rowNormHisto.GetNbinsY()
        
        for yBin in range(1, nbins_y+1):
            totalContent = 0.0
            for xBin in range(1, nbins_x+1):
                totalContent += rowNormHisto.GetBinContent(xBin, yBin)
            if totalContent != 0.0:
                for xBin in range(1, nbins_x+1):
                    content = rowNormHisto.GetBinContent(xBin, yBin)
                    rowNormHisto.SetBinContent(xBin, yBin, content/totalContent)
        return rowNormHisto

    def columnNormalizeHistogram(self, histogram):
        histogramName = f"{histogram.GetName()}_column_norm"
        columnNormHisto = histogram.Clone()
        columnNormHisto.SetNameTitle(
            histogramName,
            histogramName,
        )
        
        nbins_x = columnNormHisto.GetNbinsX()
        nbins_y = columnNormHisto.GetNbinsY()
        
        for xBin in range(1, nbins_x+1):
            totalContent = 0.0
            for yBin in range(1, nbins_y+1):
                totalContent += columnNormHisto.GetBinContent(xBin, yBin)
            if totalContent != 0.0:
                for yBin in range(1, nbins_y+1):
                    content = columnNormHisto.GetBinContent(xBin, yBin)
                    columnNormHisto.SetBinContent(xBin, yBin, content/totalContent)
        return columnNormHisto

    def drawPlots(self):
        ROOT.gStyle.SetOptStat(0)
        fileName = self.dictOfFiles["teacherstudent"]
        theFile = ROOT.TFile(fileName)

        listOfKeys = list(theFile.GetListOfKeys())
        listOfKeys = [x.GetName() for x in listOfKeys]

        deltaScatters = {}
        absDeltaScatters = {}
        teacherAdjustedScores = {}
        teacherScores = {}
        studentScores = {}
        studentErrs = {}
        studentAbsErrs = {}

        for key in listOfKeys:
            sample, teacher, student, plotType = self.parseHistogramName(key)
            # handle the delta scatters and abs delta scatter
            if plotType == 'delta_scatter' or plotType=='abs_delta_scatter':
                if plotType == 'delta_scatter':
                    relevantDict = deltaScatters
                elif plotType == 'abs_delta_scatter':
                    relevantDict = absDeltaScatters
                    
                if sample not in relevantDict:
                    relevantDict[sample] = {}
                if teacher not in relevantDict[sample]:
                    relevantDict[sample][teacher] = {}
                if student not in relevantDict[sample][teacher]:
                    relevantDict[sample][teacher][student] = theFile.Get(key)
            #handle the teacher adjusted scores and teacher scores
            if plotType == 'teacher_adjusted_score' or plotType == 'teacher_score':
                if plotType == 'teacher_adjusted_score':
                    relevantDict = teacherAdjustedScores
                elif plotType == 'teacher_score':
                    relevantDict = teacherScores

                if sample not in relevantDict:
                    relevantDict[sample] = {}
                if teacher not in relevantDict[sample]:
                    relevantDict[sample][teacher] = theFile.Get(key)
            #handles the student scores, student errors, absolute student errors
            if plotType == 'student_score' or plotType == 'student_errors' or plotType == 'student_abs_errors':
                if plotType == 'student_score':
                    relevantDict = studentScores
                elif plotType == 'student_errors':
                    relevantDict = studentErrs
                elif plotType == 'student_abs_errors':
                    relevantDict = studentAbsErrs

                if sample not in relevantDict:
                    relevantDict[sample] = {}
                if student not in relevantDict[sample]:
                    relevantDict[sample][student] = theFile.Get(key)
        
        self.processDeltaScatters(deltaScatters, name="delta_scatter")
        self.processDeltaScatters(absDeltaScatters, name="abs_delta_scatter")
        
        self.processScores(teacherAdjustedScores, name="teacher_adjusted_score")
        self.processScores(teacherScores, name="teacher_score")
        self.processScores(studentScores, name="student_score")

        
        self.processErrors(studentErrs, name="student_errs")
        self.processErrors(studentAbsErrs, name="student_abs_errors")

    def draw2D(self, theHisto, yAxisName, xAxisName, canvasName):
        theCanvas = ROOT.TCanvas(canvasName)
        outputName = self.outputPath/f"{canvasName}.png"
        
        theHisto.Draw("COLZ TEXT")
        theHisto.GetXaxis().SetTitle(xAxisName)
        theHisto.GetYaxis().SetTitle(yAxisName)
        
        quietROOTFunc(theCanvas.SaveAs)(str(outputName))                    

    def processDeltaScatters(self, deltaScatters, name):
        for sample in deltaScatters:
            for teacher in deltaScatters[sample]:
                for student in deltaScatters[sample][teacher]:
                    theHisto = deltaScatters[sample][teacher][student]
                    
                    self.draw2D(
                        theHisto,
                        yAxisName = f"{student} Error",
                        xAxisName = "Adjusted Teacher Score",
                        canvasName = f"{sample}_xxx_{teacher}_xxx_{student}_xxx_{name}"
                    )

                    rowNormHisto = self.rowNormalizeHistogram(theHisto)
                    self.draw2D(
                        rowNormHisto,
                        yAxisName = f"{student} Error",
                        xAxisName = "Adjusted Teacher Score",
                        canvasName = f"{sample}_xxx_{teacher}_xxx_{student}_xxx_{name}_row_normalized",
                    )

                    columnNormHisto = self.columnNormalizeHistogram(theHisto)
                    self.draw2D(
                        columnNormHisto,
                        yAxisName = f"{student} Error",
                        xAxisName = "Adjusted Teacher Score",
                        canvasName = f"{sample}_xxx_{teacher}_xxx_{student}_xxx_{name}_column_normalized",
                    )
                    
                    
    def processScores(self, scores, name):
        for sample in scores:
            for score in scores[sample]:
                canvasName = f"{sample}_xxx_{score}_xxx_{name}"
                theCanvas = ROOT.TCanvas(canvasName)
                theHisto = scores[sample][score]
                outputName = self.outputPath/f"{canvasName}.png"

                try:
                    theHisto.Scale(1.0/theHisto.Integral())
                except ZeroDivisionError:
                    theHisto.Scale(0.0)

                theHisto.SetLineColor(ROOT.kRed)
                theHisto.SetLineWidth(2)

                theHisto.Draw("HIST")
                theHisto.GetXaxis().SetTitle(score)
                theHisto.GetYaxis().SetTitle("Events (normalized to 1)")

                quietROOTFunc(theCanvas.SaveAs)(str(outputName))

    def processErrors(self, errors, name):
        for sample in errors:
            for score in errors[sample]:
                canvasName = f"{sample}_xxx_{score}_xxx_{name}"
                theCanvas = ROOT.TCanvas(canvasName)
                theHisto = errors[sample][score]
                outputName = self.outputPath/f"{canvasName}.png"

                try:
                    theHisto.Scale(1.0/theHisto.Integral())
                except ZeroDivisionError:
                    theHisto.Scale(0.0)

                theHisto.SetLineColor(ROOT.kBlue)
                theHisto.SetLineWidth(2)
                
                theHisto.Draw("HIST")
                theHisto.GetXaxis().SetTitle(score)
                theHisto.GetYaxis().SetTitle("Events (normalized to 1)")

                quietROOTFunc(theCanvas.SaveAs)(str(outputName))
